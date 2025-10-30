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
export interface MqttTurbineMessage {
  turbineId: string;
  timestamp: string;
  environmental: EnvironmentalData;
  mechanical: MechanicalData;
  electrical: ElectricalData;
  status: TurbineStatus;
}

export interface MqttAlertMessage {
  turbineId: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
}

export interface MqttStatsMessage {
  totalPower: number; // kW
  activeTurbines: number;
  totalTurbines: number;
  farmEnvironmental: FarmEnvironmentalData;
  timestamp: string;
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
