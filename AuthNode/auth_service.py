# auth_service_class.py
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

import jwt
import bcrypt
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

# Ajusta la ruta si tu MongoSingleton está en otra carpeta
from Shared.MongoSingleton import MongoSingleton

# CONFIG via env
JWT_SECRET = os.environ.get("JWT_SECRET", "CAMBIA_ESTE_SECRETO")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
DEFAULT_TTL_SECONDS = int(os.environ.get("JWT_TTL", 3600))
DEFAULT_SEED_PASSWORD = os.environ.get("DEFAULT_SEED_PASSWORD", "default_password_123")

URI_BD_CONNECTION = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
# Helpers (regex)
_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")

class AuthService:
    def __init__(self):
        self.mongo = MongoSingleton.get_singleton_client(db_name="auth_db", uri=URI_BD_CONNECTION)
        self.db = self.mongo.db
        self.users_coll = self.db["users"]
        self.roles_coll = self.db["roles"]

        try:
            self.users_coll.create_index([("username", ASCENDING)], unique=True)
            self.roles_coll.create_index([("name", ASCENDING)], unique=True)
        except Exception:
            pass

    # ---------------- Password helpers ----------------
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False

    # ---------------- placeholder helpers ----------------
    @staticmethod
    def extract_placeholders(tpl: str) -> List[str]:
        return _PLACEHOLDER_RE.findall(tpl)

    @staticmethod
    def has_username_var(tpl: str) -> bool:
        return "${username}" in tpl

    @staticmethod
    def replace_username_var(tpl: str, username: str) -> str:
        if username is None:
            return tpl
        return tpl.replace("${username}", username)

    # ---------------- Roles CRUD ----------------
    def create_or_update_role(self, name: str, rules: List[Dict[str, Any]]):
        """
        rules: list of { permission, action, topic_template, sort_order (opt) }
        """
        self.roles_coll.update_one({"name": name}, {"$set": {"rules": rules}}, upsert=True)

    def get_role_rules(self, role_name: str) -> List[Dict[str, Any]]:
        doc = self.roles_coll.find_one({"name": role_name}, {"rules": 1})
        return doc.get("rules", []) if doc else []

    # ---------------- Users CRUD ----------------
    def create_user(self, username: str, password: str, roles: List[str] = None,
                    resources: List[Dict[str, Any]] = None, jwt_ttl: int = DEFAULT_TTL_SECONDS) -> Dict[str, Any]:
        """
        Crea un user. Lanza DuplicateKeyError si username ya existe.
        """
        password_hash = self.hash_password(password)
        doc = {
            "username": username,
            "password_hash": password_hash,
            "roles": roles or [],
            "resources": resources or [],
            "jwt_ttl": jwt_ttl,
            "created_at": datetime.utcnow()
        }
        self.users_coll.insert_one(doc)
        return doc

    def get_user(self, username: str) -> Dict[str, Any]:
        return self.users_coll.find_one({"username": username})

    # ---------------- Build ACLs ----------------
    def build_acls_for_user(self, username: str) -> List[Dict[str, Any]]:
        """
        Construye ACLs para un username usando roles + resources embebidos.
        Sustituye ${username} en plantillas automáticamente.
        """
        user = self.get_user(username)
        if not user:
            raise ValueError("user not found")

        resources = user.get("resources", [])
        roles = user.get("roles", [])
        acls: List[Dict[str, Any]] = []

        for role_name in roles:
            rules = self.get_role_rules(role_name)
            rules = sorted(rules, key=lambda r: r.get("sort_order", 100))

            for rule in rules:
                tpl = rule.get("topic_template")
                if not tpl:
                    continue

                placeholders = self.extract_placeholders(tpl)

                # Caso: sin placeholders -> agregar directamente (sustituir ${username} si existe)
                if len(placeholders) == 0:
                    topic = self.replace_username_var(tpl, username) if self.has_username_var(tpl) else tpl
                    acls.append({"permission": rule["permission"], "action": rule["action"], "topic": topic})
                    continue

                for res in resources:
                    candidate = {k: res[k] for k in ("farm_id", "turbine_id", "tag") if k in res}
                    missing = [p for p in placeholders if p not in candidate]

                    if not missing:
                        topic = tpl
                        for p in placeholders:
                            topic = topic.replace(f"{{{p}}}", str(candidate[p]))
                        topic = self.replace_username_var(topic, username)
                        acls.append({"permission": rule["permission"], "action": rule["action"], "topic": topic})
                        continue

                    # Heuristica: si falta turbine_id y resource.kind == 'farm' -> usar '+'
                    if len(missing) == 1 and missing[0] == "turbine_id" and res.get("kind") == "farm" and "farm_id" in res:
                        topic = tpl.replace("{turbine_id}", "+").replace("{farm_id}", str(res["farm_id"]))
                        topic = self.replace_username_var(topic, username)
                        acls.append({"permission": rule["permission"], "action": rule["action"], "topic": topic})
                        continue

        # Asegurarse de deny all al final
        if not any(a for a in acls if a["permission"] == "deny" and a["topic"] == "#"):
            acls.append({"permission": "deny", "action": "all", "topic": "#"})

        seen = set()
        uniq = []
        for a in acls:
            key = f"{a['permission']}|{a['action']}|{a['topic']}"
            if key not in seen:
                seen.add(key)
                uniq.append(a)
        return uniq

    # ---------------- Issue JWT & Authenticate ----------------
    def issue_jwt_for_user(self, username: str) -> Dict[str, Any]:
        """
        Genera y firma el JWT que incluye 'acl' expandida.
        """
        user = self.get_user(username)
        if not user:
            raise ValueError("user not found")

        ttl = user.get("jwt_ttl", DEFAULT_TTL_SECONDS)
        acls = self.build_acls_for_user(username)

        exp = datetime.utcnow() + timedelta(seconds=ttl)
        payload = {
            "username": username,
            "exp": int(exp.timestamp()),
            "acl": acls
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return {"token": token, "payload": payload}

    def authenticate_user(self, username: str, password: str) -> bool:
        user = self.users_coll.find_one({"username": username}, {"password_hash": 1})
        if not user:
            return False
        return self.verify_password(password, user["password_hash"])

    # ---------------- Seeding helpers ----------------
    @staticmethod
    def _make_turbine_username(farm_id: int, turbine_id: int) -> str:
        return f"WF-{farm_id}-T-{turbine_id}"

    def seed_roles(self):
        wind_turbine_rules = [
            {"permission": "allow", "action": "publish", "topic_template": "/farm/{farm_id}/turbine/{turbine_id}/clean_telemetry", "sort_order": 10},
            {"permission": "allow", "action": "subscribe", "topic_template": "/farm/{farm_id}/turbine/{turbine_id}/commands", "sort_order": 20},
            {"permission": "deny", "action": "all", "topic_template": "#", "sort_order": 1000}
        ]
        front_node_rules = [
            {"permission": "allow", "action": "subscribe", "topic_template": "/farm/+/turbine/+/clean_telemetry", "sort_order": 10},
            {"permission": "allow", "action": "publish", "topic_template": "/farm/+/aggregated/telemetry", "sort_order": 20},
            {"permission": "deny", "action": "all", "topic_template": "#", "sort_order": 1000}
        ]
        stat_node_rules = [
            {"permission": "allow", "action": "subscribe", "topic_template": "/farm/+/aggregated/#", "sort_order": 10},
            {"permission": "allow", "action": "publish", "topic_template": "/farm/+/stats/{metric}", "sort_order": 20},
            {"permission": "deny", "action": "all", "topic_template": "#", "sort_order": 1000}
        ]

        self.create_or_update_role("wind_turbine", wind_turbine_rules)
        self.create_or_update_role("front_node", front_node_rules)
        self.create_or_update_role("stat_node", stat_node_rules)
        print("Creacion roles o actualizacion hecha: wind_turbine, front_node, stat_node")

    def seed_users(self, farms: List[Dict[str, Any]], seed_password: str = None):
        """
        Crea usuarios WF-{farm_id}-T-{turbine_id} + front_node_usr + stat_node_usr.
        farms: [{"farm_id": 1, "turbines": [1,2,3]}, ...]
        """
        pwd = seed_password or DEFAULT_SEED_PASSWORD
        created, skipped = [], []

        # turbinas
        for farm in farms:
            farm_id = int(farm["farm_id"])
            for turbine_id in farm.get("turbines", []):
                username = self._make_turbine_username(farm_id, turbine_id)
                res = {"kind": "turbine", "farm_id": farm_id, "turbine_id": turbine_id}
                try:
                    self.create_user(username=username, password=pwd, roles=["wind_turbine"], resources=[res])
                    created.append(username)
                except DuplicateKeyError:
                    skipped.append(username)
                except Exception as e:
                    skipped.append(f"{username}: {str(e)}")

        # usuarios globales
        for uname, role in [("front_node_usr", "front_node"), ("stat_node_usr", "stat_node")]:
            try:
                self.create_user(username=uname, password=pwd, roles=[role], resources=[])
                created.append(uname)
            except DuplicateKeyError:
                skipped.append(uname)
            except Exception as e:
                skipped.append(f"{uname}: {str(e)}")

        print(f"Seeding completado. Usuarios creados: {len(created)}, omitidos: {len(skipped)}")
        return {"created": created, "skipped": skipped}
    
     # ---------------- Development helper: clear DB ----------------
    def clear_db(self, drop_collections: bool = True):
        """
        Limpia colecciones usadas por el servicio. Para facilitar pruebas.
        drop_collections=True => drop collections (elimina indices también).
        drop_collections=False => borra documentos pero mantiene índices.
        """
        if drop_collections:
            try:
                self.db.drop_collection("users")
                self.db.drop_collection("roles")
                # opcional: locks u otras colecciones que uses para seed/locks
                if "locks" in self.db.list_collection_names():
                    self.db.drop_collection("locks")
                print("DB cleared: dropped collections users, roles, locks (if present).")
            except Exception as e:
                print("Error dropping collections:", e)
        else:
            try:
                self.users_coll.delete_many({})
                self.roles_coll.delete_many({})
                if "locks" in self.db.list_collection_names():
                    self.db["locks"].delete_many({})
                print("DB cleared: deleted all documents from users, roles, locks.")
            except Exception as e:
                print("Error deleting documents:", e)

