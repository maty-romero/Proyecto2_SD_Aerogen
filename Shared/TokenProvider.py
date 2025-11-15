# token_provider.py
import time
import threading
from typing import Optional, Dict, Any
import requests
import jwt  # PyJWT

DEFAULT_TOKEN_ENDPOINT = "http://auth_node:5001/token"  # cambiar por nombre servicio/contenedor

class TokenProvider:
    """
    Obtiene y cachea tokens JWT desde un endpoint HTTP POST /token.
    - post body: {"username": "...", "password": "..."}
    - response expected: {"token": "...", ...}
    Cachea por username. Lee 'exp' claim del token para refrescarlo antes de expirar.
    Thread-safe y reintentos básicos.
    """
    def __init__(
        self,
        token_url: str = DEFAULT_TOKEN_ENDPOINT,
        timeout: float = 15.0,
        refresh_margin: int = 30,     # segundos antes de expirar para refrescar
        max_retries: int = 5,
        retry_backoff: float = 1.0
    ):
        self.token_url = token_url
        self.timeout = timeout
        self.refresh_margin = refresh_margin
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        # cache: username -> { token: str, exp_ts: int }
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def _fetch_token_from_server(self, username: str, password: str) -> Dict[str, Any]:
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    self.token_url,
                    json={"username": username, "password": password},
                    timeout=self.timeout
                )
                resp.raise_for_status()
                data = resp.json()
                token = data.get("token") or data.get("access_token")
                if not token:
                    raise ValueError("No token in response")
                # parse exp claim without verification to get expiry
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
                    exp = int(decoded.get("exp")) if decoded.get("exp") else None
                except Exception:
                    exp = None
                return {"token": token, "exp": exp, "raw": data}
            except Exception as e:
                last_err = e
                # backoff
                time.sleep(self.retry_backoff * attempt)
        raise RuntimeError(f"Failed to fetch token for {username}: {last_err}")

    def get_token(self, username: str, password: str) -> str:
        """
        Devuelve un token válido para username. Si no hay token en cache o está próximo a expirar,
        solicita uno nuevo al endpoint.
        """
        now = int(time.time())
        with self._lock:
            entry = self._cache.get(username)
            if entry:
                token = entry.get("token")
                exp = entry.get("exp")
                # if no exp provided, assume token valid and return (or refresh every call if you prefer)
                if exp is None or (exp - self.refresh_margin) > now:
                    return token
                # else expired or near expiry -> fetch new
            # no valid token cached -> fetch a new one
            result = self._fetch_token_from_server(username, password)
            token = result["token"]
            exp = result["exp"]
            # If no exp available, set a conservative TTL (e.g., 300s)
            if exp is None:
                exp = now + 300
            self._cache[username] = {"token": token, "exp": int(exp)}
            return token

    def invalidate(self, username: str):
        """Forzar invalidación de un token cached (por ejemplo, si login cambia)."""
        with self._lock:
            self._cache.pop(username, None)
