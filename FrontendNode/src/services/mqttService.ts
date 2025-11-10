import mqtt, { MqttClient } from 'mqtt';
import {
  MqttTurbineMessage, 
  MqttFlatMessage,
  MqttFlatAlert,
  MqttFlatStats,
  MqttAlertMessage, 
  MqttStatsMessage,
  TurbineStatus,
  AlertType,
  AlertSeverity,
  Turbine,
  Alert
} from '../types/turbine';

/**
 * MQTT Service para integración con EMQX
 * 
 * Este servicio gestiona la conexión con el broker MQTT EMQX
 * y maneja las suscripciones a los diferentes tópicos.
 * 
 * Tópicos esperados:
 * - windfarm/turbines/{turbineId}/measurements - Mediciones de cada molino
 * - windfarm/alerts - Alertas del sistema
 * - windfarm/stats - Estadísticas generales del parque
 */

export class MqttService {
  private client: MqttClient | null = null;
  private connected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  
  // Callbacks para manejo de datos
  private onTurbineDataCallback?: (turbineId: string, data: MqttTurbineMessage, metadata?: { name: string; capacity: number }) => void;
  private onAlertCallback?: (alert: MqttAlertMessage) => void;
  private onStatsCallback?: (stats: MqttStatsMessage) => void;
  private onConnectionChangeCallback?: (connected: boolean) => void;

  constructor(
    private brokerUrl: string = 'ws://localhost:8083/mqtt',
    private options: {
      clientId?: string;
      username?: string;
      password?: string;
      clean?: boolean;
      reconnectPeriod?: number;
    } = {}
  ) {
    this.options = {
      clientId: `windfarm_client_${Math.random().toString(16).substr(2, 8)}`,
      username: 'admin',
      password: 'public',
      clean: options.clean !== false,
      reconnectPeriod: options.reconnectPeriod || 5000,
    };
  }

  /**
   * Conecta al broker MQTT
   */
  async connect(): Promise<void> {
    try {
      console.log('Conectando a MQTT broker:', this.brokerUrl);
      
      this.client = mqtt.connect(this.brokerUrl, this.options);

      this.client.on('connect', () => {
        this.connected = true;
        this.reconnectAttempts = 0;
        if (this.onConnectionChangeCallback) {
          this.onConnectionChangeCallback(true);
        }
        this.subscribeToTopics();
        console.log('Conectado a MQTT broker exitosamente');
      });

      this.client.on('message', (topic: string, payload: Buffer) => {
        this.handleMessage(topic, payload);
      });

      this.client.on('error', (error: Error) => {
        console.error('Error MQTT:', error);
        // La reconexión es manejada por el evento 'close'
      });

      this.client.on('close', () => {
        if (this.connected) {
          this.connected = false;
          if (this.onConnectionChangeCallback) {
            this.onConnectionChangeCallback(false);
          }
          console.log('Desconectado del broker MQTT. Intentando reconectar...');
          this.handleReconnect();
        }
      });

      this.client.on('offline', () => {
        console.log('Cliente MQTT está offline.');
        if (this.connected) {
          this.connected = false;
          this.onConnectionChangeCallback?.(false);
        }
      });
    } catch (error) {
      console.error('Error conectando a MQTT:', error);
      this.handleReconnect();
    }
  }

  /**
   * Suscribirse a los tópicos del sistema
   */
  private subscribeToTopics(): void {
    if (!this.connected) return;

    // Suscribirse a mediciones de todas las turbinas
    this.subscribe('windfarm/turbines/+/clean_telemetry');
    
    // Suscribirse a alertas
    this.subscribe('windfarm/alerts');
    
    // Suscribirse a estadísticas generales
    this.subscribe('windfarm/stats');
    
    console.log('Suscrito a tópicos MQTT');
  }

  /**
   * Suscribirse a un tópico específico
   */
  private subscribe(topic: string): void {
    try {
      if (!this.client) return;
      this.client.subscribe(topic, { qos: 1 }, (err) => {
        if (err) {
          console.error('Error suscribiendo al tópico:', topic, err);
        } else {
          console.log('Suscrito al tópico:', topic);
        }
      });
    } catch (error) {
      console.error('Error suscribiendo al tópico:', topic, error);
    }
  }

  /**
   * Transforma el JSON plano de alerta al formato estructurado interno
   */
  private transformFlatAlert(flatAlert: MqttFlatAlert): MqttAlertMessage {
    // Mapear tipo de alerta
    const typeMap: Record<string, AlertType> = {
      'electrical': 'electrical',
      'eléctrica': 'electrical',
      'electrica': 'electrical',
      'mechanical': 'mechanical',
      'mecánica': 'mechanical',
      'mecanica': 'mechanical',
      'environmental': 'environmental',
      'ambiental': 'environmental',
      'system': 'system',
      'sistema': 'system'
    };
    
    const type = typeMap[flatAlert.alert_type.toLowerCase()] || 'system';
    
    // Mapear severidad
    const severityMap: Record<string, AlertSeverity> = {
      'critical': 'critical',
      'crítico': 'critical',
      'critico': 'critical',
      'warning': 'warning',
      'advertencia': 'warning',
      'info': 'info',
      'información': 'info',
      'informacion': 'info'
    };
    
    const severity = severityMap[flatAlert.severity.toLowerCase()] || 'info';
    
    return {
      turbineId: String(flatAlert.turbine_id),
      type: type,
      severity: severity,
      message: flatAlert.message + (flatAlert.details ? ` - ${flatAlert.details}` : ''),
      timestamp: flatAlert.timestamp
    };
  }

  /**
   * Transforma el JSON plano de estadísticas al formato estructurado interno
   */
  private transformFlatStats(flatStats: MqttFlatStats): MqttStatsMessage {
    // Transformar producción horaria
    const hourlyProduction = flatStats.hourly_production_kwh.map((power, index) => ({
      hour: flatStats.hourly_timestamps[index] || `${index}:00`,
      power: power
    }));

    // Transformar producción semanal
    const weeklyProduction = flatStats.daily_production_kwh.map((prod, index) => ({
      day: flatStats.daily_timestamps[index] || `Día ${index + 1}`,
      production: prod
    }));

    // Transformar producción mensual
    const monthlyProduction = flatStats.monthly_production_kwh.map((prod, index) => ({
      month: flatStats.monthly_timestamps[index] || `Mes ${index + 1}`,
      production: prod
    }));

    // Transformar velocidad de viento horaria
    const hourlyWindSpeed = flatStats.hourly_avg_wind_speed.map((speed, index) => ({
      hour: flatStats.hourly_timestamps[index] || `${index}:00`,
      windSpeed: speed
    }));

    // Transformar voltaje horario
    const hourlyVoltage = flatStats.hourly_avg_voltage.map((voltage, index) => ({
      hour: flatStats.hourly_timestamps[index] || `${index}:00`,
      voltage: voltage
    }));
    
    return {
      totalPower: flatStats.total_active_power_kw,
      activeTurbines: flatStats.operational_turbines,
      totalTurbines: flatStats.total_turbines,
      farmEnvironmental: {
        avgWindSpeed: flatStats.avg_wind_speed_mps,
        maxWindSpeed: flatStats.max_wind_speed_mps,
        minWindSpeed: flatStats.min_wind_speed_mps,
        predominantWindDirection: flatStats.predominant_wind_direction_deg,
        lastUpdate: flatStats.timestamp
      },
      timestamp: flatStats.timestamp,
      averagePowerFactor: flatStats.avg_power_factor,
      averageVoltage: flatStats.avg_voltage_v,
      
      // Datos para gráficos
      hourlyProduction: hourlyProduction,
      weeklyProduction: weeklyProduction,
      monthlyProduction: monthlyProduction,
      hourlyWindSpeed: hourlyWindSpeed,
      hourlyVoltage: hourlyVoltage
    };
  }

  /**
   * Transforma el JSON plano del molino al formato estructurado interno
   */
  private transformFlatMessage(flatMsg: MqttFlatMessage): MqttTurbineMessage {
    // Mapear estado del molino a TurbineStatus
    const statusMap: Record<string, TurbineStatus> = {
      'operational': 'operational',
      'running': 'operational',
      'stopped': 'stopped',
      'fault': 'fault',
      'error': 'fault',
      'maintenance': 'maintenance',
      'standby': 'standby',
      'idle': 'standby'
    };
    
    const status = statusMap[flatMsg.operational_state.toLowerCase()] || 'standby';
    
    // Calcular factor de potencia
    const apparentPower = Math.sqrt(
      flatMsg.active_power_kw ** 2 + flatMsg.reactive_power_kvar ** 2
    );
    const powerFactor = apparentPower > 0 
      ? flatMsg.active_power_kw / apparentPower 
      : 0;
    
    return {
      turbineId: String(flatMsg.turbine_id),
      timestamp: flatMsg.timestamp,
      environmental: {
        windSpeed: flatMsg.wind_speed_mps,
        windDirection: flatMsg.wind_direction_deg
      },
      mechanical: {
        rotorSpeed: flatMsg.rotor_speed_rpm,
        pitchAngle: flatMsg.blade_pitch_angle_deg,
        yawPosition: flatMsg.yaw_position_deg,
        vibration: flatMsg.vibrations_mms,
        gearboxTemperature: flatMsg.gear_temperature_c,
        bearingTemperature: flatMsg.bearing_temperature_c,
        oilPressure: 5.0, // Valor por defecto - agregar al JSON si está disponible
        oilLevel: 85 // Valor por defecto - agregar al JSON si está disponible
      },
      electrical: {
        outputVoltage: flatMsg.output_voltage_v,
        outputCurrent: flatMsg.generated_current_a,
        activePower: flatMsg.active_power_kw,
        reactivePower: flatMsg.reactive_power_kvar,
        powerFactor: powerFactor
      },
      status: status
    };
  }

  /**
   * Maneja mensajes MQTT entrantes
   */
  private handleMessage(topic: string, payload: Buffer): void {
    try {
      // --- INICIO: Log para depuración ---
      console.log(`[MQTT INCOMING] Topic: ${topic} | Payload: ${payload.toString()}`);
      // --- FIN: Log para depuración ---
      const message = JSON.parse(payload.toString());
      
      // Procesar según el tópico
      if (topic.startsWith('windfarm/turbines/') && topic.endsWith('/clean_telemetry')) {
        // Mensaje plano del molino - transformar antes de procesar
        const flatMsg = message as MqttFlatMessage;
        const turbineId = String(flatMsg.turbine_id);
        const structuredMessage = this.transformFlatMessage(flatMsg);
        const metadata = {
          name:  flatMsg.turbine_name,
          capacity: flatMsg.capacity_mw
        };
        this.handleTurbineMessage(turbineId, structuredMessage, metadata);
      } else if (topic === 'windfarm/alerts') {
        // Mensaje plano de alerta - transformar antes de procesar
        const flatAlert = message as MqttFlatAlert;
        const structuredAlert = this.transformFlatAlert(flatAlert);
        this.handleAlertMessage(structuredAlert);
      } else if (topic === 'windfarm/stats') {
        // Mensaje plano de estadísticas - transformar antes de procesar
        console.log('[STATS RECEIVED]', message);
        const flatStats = message as MqttFlatStats;
        const structuredStats = this.transformFlatStats(flatStats);
        this.handleStatsMessage(structuredStats);
      }
    } catch (error) {
      console.error('Error procesando mensaje MQTT:', error);
    }
  }

  /**
   * Procesa mensajes de mediciones de turbinas
   */
  private handleTurbineMessage(turbineId: string, message: MqttTurbineMessage, metadata?: { name: string; capacity: number }): void {
    if (this.onTurbineDataCallback) {
      this.onTurbineDataCallback(turbineId, message, metadata);
    }
  }

  /**
   * Procesa mensajes de alertas
   */
  private handleAlertMessage(message: MqttAlertMessage): void {
    if (this.onAlertCallback) {
      this.onAlertCallback(message);
    }
  }

  /**
   * Procesa mensajes de estadísticas
   */
  private handleStatsMessage(message: MqttStatsMessage): void {
    if (this.onStatsCallback) {
      this.onStatsCallback(message);
    }
  }

  /**
   * Maneja reconexión automática
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reintentando conexión (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.options.reconnectPeriod);
    } else {
      console.error('Máximo de reintentos de conexión alcanzado');
    }
  }

  /**
   * Desconecta del broker
   */
  disconnect(): void {
    if (this.client) {
      this.client.end();
      this.connected = false;
      if (this.onConnectionChangeCallback) {
        this.onConnectionChangeCallback(false);
      }
      console.log('Desconectado del broker MQTT');
    }
  }

  /**
   * Registra callback para datos de turbinas
   */
  onTurbineData(callback: (turbineId: string, data: MqttTurbineMessage, metadata?: { name: string; capacity: number }) => void): void {
    this.onTurbineDataCallback = callback;
  }

  /**
   * Registra callback para alertas
   */
  onAlert(callback: (alert: MqttAlertMessage) => void): void {
    this.onAlertCallback = callback;
  }

  /**
   * Registra callback para estadísticas
   */
  onStats(callback: (stats: MqttStatsMessage) => void): void {
    this.onStatsCallback = callback;
  }

  /**
   * Registra callback para cambios de conexión
   */
  onConnectionChange(callback: (connected: boolean) => void): void {
    this.onConnectionChangeCallback = callback;
  }

  /**
   * Publica un mensaje en un tópico (para comandos/control)
   */
  publish(topic: string, message: any): void {
    if (!this.connected || !this.client) {
      console.error('No conectado al broker MQTT');
      return;
    }
    
    try {
      const payload = JSON.stringify(message);
      this.client.publish(topic, payload, { qos: 1 }, (err) => {
        if (err) {
          console.error('Error publicando mensaje:', err);
        } else {
          console.log('Mensaje publicado en', topic);
        }
      });
    } catch (error) {
      console.error('Error publicando mensaje:', error);
    }
  }

  /**
   * Verifica si está conectado
   */
  isConnected(): boolean {
    return this.connected;
  }
}

// Instancia singleton del servicio MQTT
let mqttServiceInstance: MqttService | null = null;

export const getMqttService = (
  brokerUrl?: string,
  options?: any
): MqttService => {
  if (!mqttServiceInstance) {
    mqttServiceInstance = new MqttService(brokerUrl, options);
  }
  return mqttServiceInstance;
};
