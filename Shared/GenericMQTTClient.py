import json
import time
from typing import Optional
import paho.mqtt.client as mqtt
import os

from Shared.TokenProvider import TokenProvider

# -- Constantes configuracion
# Si corremos en Docker, usamos el nombre del servicio. Si no, localhost.
#BROKER_HOST = "localhost"
BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = 1883

class GenericMQTTClient:
    """
    Cliente MQTT genérico y reutilizable.
    NO contiene nada específico de turbinas ni payloads.
    Métodos: connect, disconnect, publish, set_lwt, clear_retained.
    """
    def __init__(self, client_id: str = None, broker_host: str = BROKER_HOST, broker_port: int = BROKER_PORT, token_provider: TokenProvider = None):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self._client_id = client_id or ""    
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        # Config Autenticacion 
        self.token_provider = token_provider
        self._auth_username: Optional[str] = None
        self._auth_password: Optional[str] = None

    def set_auth_credentials(self, username: str, password: str):
        self._auth_username = username
        self._auth_password = password

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"[MQTT:{self._client_id}] connected rc={rc}")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        print(f"[MQTT:{self._client_id}] disconnected rc={rc}")

    def set_lwt(self, topic: str, payload, qos: int = 1, retain: bool = True):
        """
        Configura el LWT para este cliente.
        payload puede ser dict/str/bytes; si no es str/bytes se JSONifica.
        """
        if not isinstance(payload, (str, bytes)):
            payload = json.dumps(payload)
        self.client.will_set(topic, payload=payload, qos=qos, retain=retain)

    def connect(self, keepalive: int = 60, max_retries: int = 5, retry_delay_s: int = 3):
        # si existe token_provider y credenciales, obtener token JWT y se usa como password
        if self.token_provider and self._auth_username and self._auth_password:
            try:
                token = self.token_provider.get_token(self._auth_username, self._auth_password)
                self.client.username_pw_set(username=self._auth_username, password=token)
                print(f"[MQTT:{self._client_id}] Using JWT for username='{self._auth_username}'")
            except Exception as e:
                print(f"[MQTT:{self._client_id}] Failed to obtain token: {e}")
        
        """
        Conecta y arranca el loop, con reintentos en caso de fallo inicial.
        Asume que set_lwt() (si se necesita) fue llamado antes.
        """
        retries = 0
        while retries < max_retries:
            try:
                print(f"[MQTT:{self._client_id}] connecting to {self.broker_host}:{self.broker_port} ... (Attempt {retries + 1})")
                self.client.connect(self.broker_host, self.broker_port, keepalive=keepalive)
                self.client.loop_start()
                return
            except ConnectionRefusedError as e:
                print(f"[MQTT:{self._client_id}] Connection refused. Retrying in {retry_delay_s}s...")
                retries += 1
                time.sleep(retry_delay_s)
        raise ConnectionRefusedError(f"Failed to  connect to MQTTbroker after {max_retries} attempts.")


    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False):
        """
        Publica en cualquier topic. Payload se serializa a JSON si no es str/bytes.
        """
        if not isinstance(payload, (str, bytes)):
            payload = json.dumps(payload)
        self.client.publish(topic, payload=payload, qos=qos, retain=retain)
        print(f"--- Publicado en '{topic}': \n{payload}\n")

    def clear_retained(self, topic: str):
        """Limpia el mensaje retenido en 'topic' (publicando un payload vacío con retain=True)."""
        self.client.publish(topic, payload="", retain=True)

    def subscribe(self, topic: str, callback, qos: int = 0):
        # Suscription & register a callback method to handle incoming messages
        self.client.on_message = callback
        self.client.subscribe(topic, qos=qos)
        print(f"[MQTT:{self._client_id}] suscrito a '{topic}' con QoS={qos}")


    def disconnect(self):
        """Detiene loop y desconecta. No asume limpieza de topics (eso lo decide el caller)."""
        self.client.loop_stop()
        self.client.disconnect()


"""
Ejemplo uso GenericMQTTClient - Como Suscriptor

def message_handler(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        data = payload
    print(f"Recibido en '{msg.topic}': {data}")

# Instancia genérica
mqtt_sub = GenericMQTTClient(client_id="subscriber1")

# Conectar al broker
mqtt_sub.connect()

# Suscribirse a un topic
mqtt_sub.subscribe("farm/turbine/telemetry", message_handler)

# Mantener el loop activo (en un script simple)
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mqtt_sub.disconnect()

"""
