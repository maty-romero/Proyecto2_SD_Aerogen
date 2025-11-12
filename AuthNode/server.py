import os
from flask import Flask, request, jsonify
from AuthNode.auth_service import AuthService

svc = AuthService()

if os.environ.get("CLEAN_DB_ON_STARTUP", "false").lower() in ("1", "true", "yes"):
    svc.clear_db(drop_collections=True) # Limpiar DB para arranque limpio 
    # Seed roles y usuarios
    svc.seed_roles() 
    farms = [{"farm_id": 1, "turbines": [1, 2]}, {"farm_id": 2, "turbines": [1]}]
    svc.seed_users(farms=farms, seed_password=os.environ.get("DEFAULT_SEED_PASSWORD", "MiPassComun123"))

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Auth service</h1>'

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    if not all(k in data for k in ("username", "password")):
        return jsonify({"message": "username and password required"}), 400
    try:
        svc.create_user(username=data["username"], password=data["password"],
                        roles=data.get("roles", []), resources=data.get("resources", []))
        return jsonify({"message": "user created", "username": data["username"]}), 201
    # except DuplicateKeyError:
    #     return jsonify({"message": "username already exists"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


"""
Clientes deben enviar credenciales, por ejemplo: 
{
    "username": "stat_node_usr",
    "password":"MiPassComun123"  --> Password comun para todos los usuarios seedeados por ahora 
}
"""
@app.route('/token', methods=['POST'])
def token():
    data = request.json or {}
    username = data.get("username"); password = data.get("password")
    if not username or not password:
        return jsonify({"message": "username and password required"}), 400
    if not svc.authenticate_user(username, password):
        return jsonify({"message": "invalid credentials"}), 401
    res = svc.issue_jwt_for_user(username)
    return jsonify(res), 200



if __name__ == "__main__":
    app.run()
