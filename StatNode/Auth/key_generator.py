# Generacion de API KEYS seguras para el acceso a StatNode
import secrets
from werkzeug.security import generate_password_hash

def new_key(kid=None):
    raw = secrets.token_urlsafe(32)  # clave segura (~43 chars)
    kid = kid or secrets.token_hex(4)  # id corto
    combined = f"{kid}.{raw}"
    hashed = generate_password_hash(raw)  # almacena solo esto
    print("=== NUEVA API KEY ===")
    print("KID:", kid)
    print("RAW (mostrar una sola vez, cópialo al frontend):", combined)
    print("HASH (pegar en ENV/API_KEYS):", hashed)
    print("=====================")

if __name__ == "__main__":
    new_key()

"""
Ejemplo de salida --> Guardar key 
KID: 1a2b
RAW: 1a2b.Sf3A... 
HASH: pbkdf2:sha256:150000$...

"""