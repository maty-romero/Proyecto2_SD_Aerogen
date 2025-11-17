import json
import os
import time
from threading import Lock, Thread
from typing import Dict, Any

from Shared.GenericMQTTClient import GenericMQTTClient
from Shared.TokenProvider import TokenProvider
from StatNode.DB.TelemetryDB import TelemetryDB

CLEAN_TELEMETRY_TOPIC = "farms/{farm_id}/turbines/+/clean_telemetry".format(farm_id=1)
STATS_TOPIC = "farms/{farm_id}/stats".format(farm_id=1)
ALERTS_TOPIC = "farms/{farm_id}/alerts".format(farm_id=1)

class StatNode:
    # El StatNode ahora es agnóstico al farm_id, pero lo usará para las consultas. Asumimos farm_id=1 por defecto.
    def __init__(self, client_id: str = "stat_node_client"):
        self.mqtt_client = GenericMQTTClient(client_id=client_id, token_provider=TokenProvider()) 
        self.mqtt_client.set_auth_credentials(username=client_id, password="MiPassComun123")
        
        self.turbines_data = {}
        self.data_lock = Lock()
        self.publish_interval = 10  # Publicar estadísticas cada 10 segundos
        self._stop_event = False

        # Instancia del servicio de base de datos
        self.db_clients = []

    def _initialize_db_clients(self):
        """Inicializa los clientes de base de datos a partir de la variable de entorno MONGO_URIS."""
        uris_str = os.environ.get("MONGO_URIS")
        if not uris_str:
            print("[StatNode] CRÍTICO: La variable de entorno MONGO_URIS no está definida.")
            return False

        uris = [uri.strip() for uri in uris_str.split(',')]
        print(f"[StatNode] Se encontraron {len(uris)} URIs de base de datos.")

        for uri in uris:
            print(f"[StatNode] Inicializando cliente para la BD en {uri}...")
            # Asumimos que TelemetryDB() intenta conectar en su __init__ y puede fallar
            try:
                client = TelemetryDB(uri=uri)
                # Delegamos la lógica de conexión y reintentos a la propia clase
                client.connect() 
                self.db_clients.append(client)
            except Exception as e:
                print(f"[StatNode] ADVERTENCIA: No se pudo conectar a la BD en {uri}. Error: {e}")

        if not self.db_clients:
            return False

        return True



    def _message_callback(self, client, userdata, msg):
        """Callback para procesar mensajes que pueden ser telemetría o alertas,
        sin contemplar mensajes envueltos bajo 'payload'.
        """
        try:
            payload = json.loads(msg.payload.decode())
        except Exception as e:
            print(f"[StatNode] Error procesando mensaje (JSON inválido): {e}")
            return

        # --- CASO 1: ALERTA ---
        if payload.get("alert_type") is not None:
            print(f"[StatNode] ALERTA recibida (topic={msg.topic}): {payload}")

            for i, db_client in enumerate(self.db_clients):
                try:
                    db_client.insert_alerts(payload)
                except Exception as e:
                    print(f"[StatNode] CRÍTICO: Falló la escritura de ALERTA en nodo BD {i} ({db_client.uri}): {e}")

            return  # No seguimos a lógica de telemetría

        # --- CASO 2: TELEMETRIA ---
        for i, db_client in enumerate(self.db_clients):
            try:
                db_client.insert_telemetry(payload)
            except Exception as e:
                print(f"[StatNode] CRÍTICO: Falló la escritura de TELEMETRÍA en nodo BD {i} ({db_client.uri}): {e}")

        # Actualizar cache de estado en memoria
        turbine_id = payload.get("turbine_id")
        if turbine_id is not None:
            try:
                with self.data_lock:
                    self.turbines_data[turbine_id] = payload
            except Exception as e:
                print(f"[StatNode] Error actualizando turbines_data: {e}")


    def _get_turbine_counts_by_state(self) -> Dict[str, int]:
        """Cuenta las turbinas por estado operacional a partir de los datos en memoria."""
        states = {
            "operational": 0,
            "stopped": 0,
            "fault": 0,
            "maintenance": 0,
            "standby": 0,
            "unknown": 0
        }
        with self.data_lock:
            for data in self.turbines_data.values():
                state = data.get("operational_state", "unknown")
                if state in states:
                    states[state] += 1
                else:
                    states["unknown"] += 1
        return states

    def _execute_read_with_failover(self, read_operation, *args, **kwargs):
        """
        Ejecuta una operación de lectura, intentando con cada cliente de BD hasta que una sea exitosa.
        """
        for i, client in enumerate(self.db_clients):
            try:
                # Llama a la función de lectura (ej. get_metrics_farm) en el cliente actual
                result = read_operation(client, *args, **kwargs)
                # Si la lectura es exitosa, la retornamos
                return result
            except Exception as e:
                print(f"[StatNode] ADVERTENCIA: Falló la lectura en el nodo de BD {i} ({client.uri}). Intentando con el siguiente. Error: {e}")
        
        print("[StatNode] CRÍTICO: Fallaron las operaciones de lectura en todos los nodos de BD.")
        return None

    def _publish_stats(self):
        """Calcula y publica las estadísticas agregadas del parque eólico."""
        while not self._stop_event:
            time.sleep(self.publish_interval)
            farm_id = 1

            # --- LECTURAS CON FAILOVER ---
            farm_metrics = self._execute_read_with_failover(lambda c, **k: c.get_metrics_farm(**k), farm_id=farm_id, minutes=5)
            if not farm_metrics:
                print("[StatNode] No hay suficientes datos en la BD para calcular métricas del parque.")
                continue

            # Las demás lecturas también usarán el mecanismo de failover
            hourly_data = self._execute_read_with_failover(lambda c, **k: c.get_hourly_production_last_24h(**k), farm_id=farm_id)
            daily_data = self._execute_read_with_failover(lambda c, **k: c.get_daily_production_last_7_days(**k), farm_id=farm_id)
            monthly_data = self._execute_read_with_failover(lambda c, **k: c.get_monthly_production_last_12_months(**k), farm_id=farm_id)
            wind_speed_data = self._execute_read_with_failover(lambda c, **k: c.get_hourly_avg_windspeed_last_24h(**k), farm_id=farm_id)
            voltage_data = self._execute_read_with_failover(lambda c, **k: c.get_hourly_avg_voltage_last_24h(**k), farm_id=farm_id)

            # 6. Obtener conteo de turbinas por estado desde la memoria (más rápido y en tiempo real)
            turbine_counts = self._get_turbine_counts_by_state()
            total_turbines = len(self.turbines_data)

            # Construir el payload de estadísticas de acuerdo a la documentación del frontend
            stats_payload = {
                # --- Identificación y estado general ---
                "farm_id": farm_id,
                "total_turbines": total_turbines,
                "operational_turbines": turbine_counts.get("operational", 0),
                "turbine_counts_by_state": turbine_counts,

                # --- Métricas agregadas del parque (de la BD) ---
                # Usamos .get() para evitar KeyErrors si una métrica no se puede calcular
                # NOTA: El frontend esperaba 'total_active_power_kw', pero el valor es un promedio.
                # Se renombra a 'avg_active_power_kw' para mayor claridad.
                "avg_active_power_kw": farm_metrics.get("avg_power_kw"),
                "total_energy_kwh": farm_metrics.get("total_energy_kwh"),
                "avg_wind_speed_mps": farm_metrics.get("avg_wind_speed_mps"),
                "max_wind_speed_mps": farm_metrics.get("max_wind_speed_mps"),
                "min_wind_speed_mps": farm_metrics.get("min_wind_speed_mps"),
                "avg_power_factor": farm_metrics.get("avg_power_factor"),
                "avg_voltage_v": farm_metrics.get("avg_voltage_v"),
                "farm_availability_pct": farm_metrics.get("farm_availability_pct"), # Disponibilidad instantánea
                "time_based_availability_pct": farm_metrics.get("time_based_availability_pct"), # Disponibilidad en el tiempo (más precisa)
                "farm_cp_weighted": farm_metrics.get("farm_cp_weighted"), # Coeficiente de potencia ponderado
                # "predominant_wind_direction_deg": farm_metrics.get("predominant_wind_direction_deg"), # Nota: Esto no se calcula aún

                # --- Datos para gráficos (lista de objetos {timestamp, value}) ---
                "hourly_production_chart": hourly_data,
                "daily_production_chart": daily_data,
                "monthly_production_chart": monthly_data,
                "hourly_wind_speed_chart": wind_speed_data,
                "hourly_voltage_chart": voltage_data
            }

            self.mqtt_client.publish(STATS_TOPIC, stats_payload, qos=1)
            print(f"[StatNode] Estadísticas publicadas: {turbine_counts.get('operational', 0)}/{total_turbines} activas.")
    
    def run(self):
        """Inicia el StatNode."""
        print("--- [StatNode] Iniciando nodo de estadísticas ---")
        self.mqtt_client.connect()

        # --- Verificación de Conexión a BD ---
        if not self._initialize_db_clients():
            print("[StatNode] CRÍTICO: No se pudo inicializar ninguna conexión a la base de datos.")
            alert_payload = {
                "level": "critical",
                "service": "StatNode",
                "message": "No se pudo conectar a ninguna base de datos configurada. El servicio no puede operar.",
                "timestamp": time.time()
            }
            self.mqtt_client.publish(ALERTS_TOPIC, alert_payload, qos=1)
            self.stop()
            return # Detener la ejecución

        self.mqtt_client.subscribe(
            CLEAN_TELEMETRY_TOPIC,
            self._message_callback,
            qos=1
        )
        self.mqtt_client.subscribe(
            ALERTS_TOPIC,
            self._message_callback,
            qos=1
        )
        print(f"--- [StatNode] Suscrito a: {CLEAN_TELEMETRY_TOPIC} ---")
        print(f"--- [StatNode] Suscrito a: {ALERTS_TOPIC} ---")

        # Iniciar el hilo para publicar estadísticas
        stats_thread = Thread(target=self._publish_stats, daemon=True)
        stats_thread.start()

    def stop(self):
        """Detiene el StatNode."""
        print("--- [StatNode] Deteniendo nodo de estadísticas ---")
        self._stop_event = True
        self.mqtt_client.disconnect()

if __name__ == '__main__':
    stat_node = StatNode()
    stat_node.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # stat_node.stop()
        print("--- [StatNode] Proceso terminado. ---")