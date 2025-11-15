import sys
import urllib.request

def check_health(url: str):
    """
    Realiza una petición HTTP GET a la URL dada.
    - Sale con código 0 si la respuesta es exitosa (status 2xx).
    - Sale con código 1 en caso de cualquier error o status no exitoso.
    """
    try:
        # Usamos un timeout para no esperar indefinidamente
        with urllib.request.urlopen(url, timeout=5) as response:
            if 200 <= response.status < 300:
                sys.exit(0) # Éxito
            else:
                sys.exit(1) # Falla (ej. 404, 500)
    except Exception:
        sys.exit(1) # Falla (ej. no se puede conectar, timeout)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python check_primary.py <URL>", file=sys.stderr)
        sys.exit(2)
    
    check_health(sys.argv[1])