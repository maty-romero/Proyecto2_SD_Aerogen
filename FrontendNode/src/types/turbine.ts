// Turbine status types
export type TurbineStatus = 'operational' | 'stopped' | 'fault' | 'maintenance' | 'standby';

// Alert types
export type AlertSeverity = 'critical' | 'warning' | 'info';
export type AlertType = 'electrical' | 'mechanical' | 'environmental' | 'system';

// Environmental variables (solo viento por molino)
export interface EnvironmentalData {
  windSpeed: number; // m/s
  windDirection: number; // degrees (0-360)
}

// Mechanical variables
export interface MechanicalData {
  rotorSpeed: number; // RPM
  pitchAngle: number; // degrees
  yawPosition: number; // degrees
  vibration: number; // mm/s
  gearboxTemperature: number; // °C
  bearingTemperature: number; // °C
  oilPressure: number; // bar
  oilLevel: number; // %
}

// Electrical variables
export interface ElectricalData {
  outputVoltage: number; // V
  outputCurrent: number; // A
  activePower: number; // kW
  reactivePower: number; // kVAR
  powerFactor: number; // 0-1
}

// Complete turbine data
export interface Turbine {
  id: string;
  name: string;
  status: TurbineStatus;
  capacity: number; // MW
  
  // Categorized data
  environmental: EnvironmentalData;
  mechanical: MechanicalData;
  electrical: ElectricalData;
  
  // Maintenance
  lastMaintenance: string;
  nextMaintenance: string;
  operatingHours: number;
}

// Alert interface
export interface Alert {
  id: string;
  turbineId: string;
  turbineName: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  resolvedAt?: string;
}

// Farm-wide environmental data (promedios y datos generales)
export interface FarmEnvironmentalData {
  avgWindSpeed: number; // m/s
  maxWindSpeed: number; // m/s
  minWindSpeed: number; // m/s
  predominantWindDirection: number; // degrees
  lastUpdate: string;
}

// Historical data point
export interface HistoricalDataPoint {
  timestamp: string;
  turbineId: string;
  activePower: number; // kW
  windSpeed: number; // m/s
  status: TurbineStatus;
}

// MQTT message types

// Formato plano que viene del molino (single-level JSON)
export interface MqttFlatMessage {
  // Identificación
  farm_id: number;
  farm_name: string;
  turbine_id: number;
  turbine_name: string;
  timestamp: string;
  
  // Variables ambientales
  wind_speed_mps: number;
  wind_direction_deg: number;
  
  // Variables mecánicas
  rotor_speed_rpm: number;
  blade_pitch_angle_deg: number;
  yaw_position_deg: number;
  vibrations_mms: number;
  gear_temperature_c: number;
  bearing_temperature_c: number;
  
  // Variables eléctricas
  output_voltage_v: number;
  generated_current_a: number;
  active_power_kw: number;
  reactive_power_kvar: number;
  
  // Estado
  operational_state: string;
  
  // Capacidad
  capacity_mw: number;
}

// Formato estructurado (usado internamente)
export interface MqttTurbineMessage {
  turbineId: string;
  timestamp: string;
  environmental: EnvironmentalData;
  mechanical: MechanicalData;
  electrical: ElectricalData;
  status: TurbineStatus;
}

// Formato plano de alerta que viene del broker (single-level JSON)
export interface MqttFlatAlert {
  alert_id: string;
  farm_id: number;
  turbine_id: number;
  turbine_name: string;
  alert_type: string; // 'electrical', 'mechanical', 'environmental', 'system'
  severity: string; // 'critical', 'warning', 'info'
  message: string;
  details?: string;
  timestamp: string;
  acknowledged: boolean;
  resolved: boolean;
}

// Formato plano de estadísticas del parque (single-level JSON)
export interface MqttFlatStats {
  farm_id: number;
  farm_name: string;
  timestamp: string;
  
  // Producción total
  total_active_power_kw: number;
  total_reactive_power_kvar: number;
  
  // Contadores de turbinas
  total_turbines: number;
  operational_turbines: number;
  stopped_turbines: number;
  maintenance_turbines: number;
  fault_turbines: number;
  
  // Estadísticas de viento
  avg_wind_speed_mps: number;
  max_wind_speed_mps: number;
  min_wind_speed_mps: number;
  predominant_wind_direction_deg: number;
  
  // Promedios eléctricos
  avg_power_factor: number;
  avg_voltage_v: number;
  
  // Producción histórica (últimas 24 horas)
  hourly_production_kwh: number[]; // Array de 24 valores
  hourly_timestamps: string[]; // Array de 24 timestamps
}

// Formato estructurado de alerta (usado internamente)
export interface MqttAlertMessage {
  turbineId: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
}

// Formato estructurado de estadísticas (usado internamente)
export interface MqttStatsMessage {
  totalPower: number; // kW
  activeTurbines: number;
  totalTurbines: number;
  farmEnvironmental: FarmEnvironmentalData;
  timestamp: string;
  hourlyProduction?: { hour: string; power: number }[];
  averagePowerFactor?: number;
  averageVoltage?: number;
}

// API Response types
export interface ApiHistoricalResponse {
  turbineId: string;
  data: HistoricalDataPoint[];
  from: string;
  to: string;
}

export interface ApiAlertsHistoryResponse {
  alerts: Alert[];
  total: number;
  page: number;
  pageSize: number;
}
