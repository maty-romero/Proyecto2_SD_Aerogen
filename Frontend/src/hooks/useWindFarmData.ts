import { useState, useEffect, useCallback } from 'react';
import { 
  Turbine, 
  Alert, 
  MqttTurbineMessage, 
  MqttAlertMessage,
  MqttStatsMessage,
  FarmEnvironmentalData 
} from '../types/turbine';
import { getMqttService } from '../services/mqttService';
import { getApiService } from '../services/apiService';

/**
 * Hook personalizado para gestionar datos del parque eólico
 * 
 * Este hook integra:
 * - Datos en tiempo real vía MQTT
 * - Datos históricos vía API REST
 * - Estado de conexión
 * - Gestión de alertas
 */

interface UseWindFarmDataOptions {
  mqttBrokerUrl?: string;
  mqttUsername?: string;
  mqttPassword?: string;
  apiBaseUrl?: string;
  apiKey?: string;
  autoConnect?: boolean;
}

interface WindFarmData {
  turbines: Map<string, Turbine>;
  alerts: Alert[];
  farmStats: {
    totalPower: number;
    activeTurbines: number;
    totalTurbines: number;
    averagePowerFactor?: number;
    averageVoltage?: number;
  } | null;
  farmEnvironmental: FarmEnvironmentalData | null;
  hourlyProduction: { hour: string; power: number }[];
  isConnected: boolean;
  lastUpdate: Date | null;
}

export const useWindFarmData = (options: UseWindFarmDataOptions = {}) => {
  const {
    mqttBrokerUrl,
    mqttUsername,
    mqttPassword,
    apiBaseUrl,
    apiKey,
    autoConnect = false
  } = options;

  const [data, setData] = useState<WindFarmData>({
    turbines: new Map(),
    alerts: [],
    farmStats: null,
    farmEnvironmental: null,
    hourlyProduction: [],
    isConnected: false,
    lastUpdate: null,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mqttService = getMqttService(mqttBrokerUrl, {
    username: mqttUsername,
    password: mqttPassword,
  });

  const apiService = getApiService(apiBaseUrl, apiKey);

  /**
   * Maneja actualizaciones de datos de turbinas desde MQTT
   */
  const handleTurbineUpdate = useCallback((
    turbineId: string, 
    message: MqttTurbineMessage,
    metadata?: { name: string; capacity: number }
  ) => {
    setData(prev => {
      const turbines = new Map(prev.turbines);
      
      // Obtener turbina existente o crear una nueva
      const existingTurbine = turbines.get(turbineId);
      
      const updatedTurbine: Turbine = {
        id: turbineId,
        name: metadata?.name || existingTurbine?.name || `Turbina ${turbineId}`,
        status: message.status,
        capacity: metadata?.capacity || existingTurbine?.capacity || 2.5,
        environmental: message.environmental,
        mechanical: message.mechanical,
        electrical: message.electrical,
        lastMaintenance: existingTurbine?.lastMaintenance || '',
        nextMaintenance: existingTurbine?.nextMaintenance || '',
        operatingHours: existingTurbine?.operatingHours || 0,
      };
      
      turbines.set(turbineId, updatedTurbine);
      
      return {
        ...prev,
        turbines,
        lastUpdate: new Date(),
      };
    });
  }, []);

  /**
   * Maneja nuevas alertas desde MQTT
   */
  const handleAlertUpdate = useCallback((message: MqttAlertMessage) => {
    const newAlert: Alert = {
      id: `alert-${Date.now()}-${Math.random()}`,
      turbineId: message.turbineId,
      turbineName: `Turbina ${message.turbineId}`,
      type: message.type,
      severity: message.severity,
      message: message.message,
      timestamp: message.timestamp,
      acknowledged: false,
    };

    setData(prev => ({
      ...prev,
      alerts: [newAlert, ...prev.alerts].slice(0, 100), // Mantener últimas 100 alertas
      lastUpdate: new Date(),
    }));
  }, []);

  /**
   * Maneja actualizaciones de estadísticas generales desde MQTT
   */
  const handleStatsUpdate = useCallback((message: MqttStatsMessage) => {
    setData(prev => ({
      ...prev,
      farmStats: {
        totalPower: message.totalPower,
        activeTurbines: message.activeTurbines,
        totalTurbines: message.totalTurbines,
        averagePowerFactor: message.averagePowerFactor,
        averageVoltage: message.averageVoltage,
      },
      farmEnvironmental: message.farmEnvironmental,
      hourlyProduction: message.hourlyProduction || [],
      lastUpdate: new Date(),
    }));
  }, []);

  /**
   * Maneja cambios de conexión MQTT
   */
  const handleConnectionChange = useCallback((connected: boolean) => {
    setData(prev => ({
      ...prev,
      isConnected: connected,
    }));
    
    if (!connected) {
      setError('Conexión perdida con el broker MQTT');
    } else {
      setError(null);
    }
  }, []);

  /**
   * Conecta al broker MQTT
   */
  const connect = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Registrar callbacks
      mqttService.onTurbineData(handleTurbineUpdate);
      mqttService.onAlert(handleAlertUpdate);
      mqttService.onStats(handleStatsUpdate);
      mqttService.onConnectionChange(handleConnectionChange);
      
      // Conectar
      await mqttService.connect();
      
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error conectando a MQTT');
      setLoading(false);
    }
  }, [mqttService, handleTurbineUpdate, handleAlertUpdate, handleStatsUpdate, handleConnectionChange]);

  /**
   * Desconecta del broker MQTT
   */
  const disconnect = useCallback(() => {
    mqttService.disconnect();
  }, [mqttService]);

  /**
   * Obtiene histórico de una turbina
   */
  const getTurbineHistory = useCallback(async (
    turbineId: string,
    from: Date,
    to: Date
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const history = await apiService.getTurbineHistory(turbineId, from, to);
      setLoading(false);
      return history;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error obteniendo histórico');
      setLoading(false);
      throw err;
    }
  }, [apiService]);

  /**
   * Obtiene histórico de alertas
   */
  const getAlertsHistory = useCallback(async (
    page: number = 1,
    pageSize: number = 50,
    severity?: string
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const history = await apiService.getAlertsHistory(page, pageSize, severity);
      setLoading(false);
      return history;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error obteniendo histórico de alertas');
      setLoading(false);
      throw err;
    }
  }, [apiService]);

  /**
   * Reconoce una alerta
   */
  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      await apiService.acknowledgeAlert(alertId);
      
      // Actualizar estado local
      setData(prev => ({
        ...prev,
        alerts: prev.alerts.map(alert =>
          alert.id === alertId ? { ...alert, acknowledged: true } : alert
        ),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error reconociendo alerta');
      throw err;
    }
  }, [apiService]);

  /**
   * Resuelve una alerta
   */
  const resolveAlert = useCallback(async (alertId: string) => {
    try {
      await apiService.resolveAlert(alertId);
      
      // Actualizar estado local
      setData(prev => ({
        ...prev,
        alerts: prev.alerts.map(alert =>
          alert.id === alertId 
            ? { ...alert, resolvedAt: new Date().toISOString() } 
            : alert
        ),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error resolviendo alerta');
      throw err;
    }
  }, [apiService]);

  /**
   * Auto-conectar si está habilitado
   */
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [autoConnect]);

  return {
    // Datos
    turbines: Array.from(data.turbines.values()),
    turbinesMap: data.turbines,
    alerts: data.alerts,
    farmStats: data.farmStats,
    farmEnvironmental: data.farmEnvironmental,
    hourlyProduction: data.hourlyProduction,
    
    // Estado
    isConnected: data.isConnected,
    loading,
    error,
    lastUpdate: data.lastUpdate,
    
    // Acciones
    connect,
    disconnect,
    getTurbineHistory,
    getAlertsHistory,
    acknowledgeAlert,
    resolveAlert,
  };
};
