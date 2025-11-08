# Especie de wrapper que valida API keys en headers de peticiones Flask
import os
import json
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import check_password_hash

# Cargar mapping kid -> hash desde ENV (API_KEYS_JSON)
_api_keys = {}
_keys_env = os.environ.get("API_KEYS_JSON")
if _keys_env:
    try:
        _api_keys = json.loads(_keys_env)
    except Exception:
        _api_keys = {}

def require_api_key():
    """
    Decorator: valida header x-api-key en formato '<kid>.<raw>'
    Si es válido, queda g.api_key_kid disponible.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            header = request.headers.get("x-api-key") or ""
            if not header:
                return jsonify({"error": "API key required"}), 401

            if "." not in header:
                return jsonify({"error": "Malformed API key"}), 401

            kid, raw = header.split(".", 1)
            entry_hash = _api_keys.get(kid)
            if not entry_hash:
                return jsonify({"error": "Invalid API key"}), 401

            try:
                if not check_password_hash(entry_hash, raw):
                    return jsonify({"error": "Invalid API key"}), 401
            except Exception:
                return jsonify({"error": "API key verification error"}), 401

            # éxito
            g.api_key_kid = kid
            # opcional: g.api_key_meta = {...} si quieres añadir info
            return f(*args, **kwargs)
        return wrapped
    return decorator
