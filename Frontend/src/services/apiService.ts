import { 
  ApiHistoricalResponse,
  ApiAlertsHistoryResponse,
  Alert,
  HistoricalDataPoint
} from '../types/turbine';

/**
 * API Service para consultas de históricos
 * 
 * Este servicio maneja las llamadas a la API REST para obtener
 * datos históricos de turbinas y alertas.
 * 
 * Endpoints esperados:
 * - GET /api/turbines/{turbineId}/history?from={timestamp}&to={timestamp}
 * - GET /api/alerts/history?page={page}&size={size}&severity={severity}
 * - GET /api/turbines/history?from={timestamp}&to={timestamp} (todos los molinos)
 */

export class ApiService {
  constructor(
    private baseUrl: string = '/api', // URL base de la API
    private apiKey?: string
  ) {}

  /**
   * Headers comunes para las peticiones
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    
    return headers;
  }

  /**
   * Maneja errores de la API
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: 'Error desconocido en la API'
      }));
      throw new Error(error.message || `Error HTTP: ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Obtiene el histórico de una turbina específica
   */
  async getTurbineHistory(
    turbineId: string,
    from: Date,
    to: Date
  ): Promise<ApiHistoricalResponse> {
    try {
      const url = new URL(`${this.baseUrl}/turbines/${turbineId}/history`, window.location.origin);
      url.searchParams.append('from', from.toISOString());
      url.searchParams.append('to', to.toISOString());
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: this.getHeaders(),
      });
      
      return this.handleResponse<ApiHistoricalResponse>(response);
    } catch (error) {
      console.error('Error obteniendo histórico de turbina:', error);
      
      // Devolver datos mock para desarrollo
      return this.getMockTurbineHistory(turbineId, from, to);
    }
  }

  /**
   * Obtiene el histórico de todas las turbinas
   */
  async getAllTurbinesHistory(
    from: Date,
    to: Date
  ): Promise<HistoricalDataPoint[]> {
    try {
      const url = new URL(`${this.baseUrl}/turbines/history`, window.location.origin);
      url.searchParams.append('from', from.toISOString());
      url.searchParams.append('to', to.toISOString());
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: this.getHeaders(),
      });
      
      return this.handleResponse<HistoricalDataPoint[]>(response);
    } catch (error) {
      console.error('Error obteniendo histórico de todas las turbinas:', error);
      
      // Devolver datos mock para desarrollo
      return this.getMockAllTurbinesHistory(from, to);
    }
  }

  /**
   * Obtiene el histórico de alertas
   */
  async getAlertsHistory(
    page: number = 1,
    pageSize: number = 50,
    severity?: string
  ): Promise<ApiAlertsHistoryResponse> {
    try {
      const url = new URL(`${this.baseUrl}/alerts/history`, window.location.origin);
      url.searchParams.append('page', page.toString());
      url.searchParams.append('size', pageSize.toString());
      
      if (severity) {
        url.searchParams.append('severity', severity);
      }
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: this.getHeaders(),
      });
      
      return this.handleResponse<ApiAlertsHistoryResponse>(response);
    } catch (error) {
      console.error('Error obteniendo histórico de alertas:', error);
      
      // Devolver datos mock para desarrollo
      return this.getMockAlertsHistory(page, pageSize);
    }
  }

  /**
   * Reconoce una alerta
   */
  async acknowledgeAlert(alertId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      
      await this.handleResponse(response);
    } catch (error) {
      console.error('Error reconociendo alerta:', error);
      throw error;
    }
  }

  /**
   * Resuelve una alerta
   */
  async resolveAlert(alertId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      
      await this.handleResponse(response);
    } catch (error) {
      console.error('Error resolviendo alerta:', error);
      throw error;
    }
  }

  // --- Métodos Mock para desarrollo ---

  private getMockTurbineHistory(
    turbineId: string,
    from: Date,
    to: Date
  ): ApiHistoricalResponse {
    const hours = Math.floor((to.getTime() - from.getTime()) / (1000 * 60 * 60));
    const data: HistoricalDataPoint[] = [];
    
    for (let i = 0; i < hours; i++) {
      const timestamp = new Date(from.getTime() + i * 60 * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        turbineId,
        activePower: 1000 + Math.random() * 1500,
        windSpeed: 8 + Math.random() * 10,
        status: Math.random() > 0.9 ? 'standby' : 'operational',
      });
    }
    
    return {
      turbineId,
      data,
      from: from.toISOString(),
      to: to.toISOString(),
    };
  }

  private getMockAllTurbinesHistory(from: Date, to: Date): HistoricalDataPoint[] {
    const hours = Math.floor((to.getTime() - from.getTime()) / (1000 * 60 * 60));
    const data: HistoricalDataPoint[] = [];
    
    for (let t = 1; t <= 24; t++) {
      const turbineId = `WT-${String(t).padStart(3, '0')}`;
      
      for (let i = 0; i < hours; i++) {
        const timestamp = new Date(from.getTime() + i * 60 * 60 * 1000);
        data.push({
          timestamp: timestamp.toISOString(),
          turbineId,
          activePower: 1000 + Math.random() * 1500,
          windSpeed: 8 + Math.random() * 10,
          status: Math.random() > 0.9 ? 'standby' : 'operational',
        });
      }
    }
    
    return data;
  }

  private getMockAlertsHistory(page: number, pageSize: number): ApiAlertsHistoryResponse {
    const total = 145;
    const alerts: Alert[] = [];
    
    for (let i = 0; i < pageSize && (page - 1) * pageSize + i < total; i++) {
      const index = (page - 1) * pageSize + i;
      const turbineNum = (index % 24) + 1;
      const severities: ('critical' | 'warning' | 'info')[] = ['critical', 'warning', 'info'];
      const types: ('electrical' | 'mechanical' | 'environmental' | 'system')[] = ['electrical', 'mechanical', 'environmental', 'system'];
      
      const severity = severities[index % 3];
      const type = types[index % 4];
      
      alerts.push({
        id: `alert-${index + 1}`,
        turbineId: `WT-${String(turbineNum).padStart(3, '0')}`,
        turbineName: `Turbina ${turbineNum}`,
        type,
        severity,
        message: this.getMockAlertMessage(type, severity),
        timestamp: new Date(Date.now() - index * 60 * 60 * 1000).toISOString(),
        acknowledged: Math.random() > 0.5,
        resolvedAt: Math.random() > 0.7 ? new Date(Date.now() - index * 30 * 60 * 1000).toISOString() : undefined,
      });
    }
    
    return {
      alerts,
      total,
      page,
      pageSize,
    };
  }

  private getMockAlertMessage(type: string, severity: string): string {
    const messages: Record<string, Record<string, string[]>> = {
      electrical: {
        critical: ['Falla en generador', 'Sobrecorriente detectada'],
        warning: ['Voltaje bajo', 'Factor de potencia subóptimo'],
        info: ['Inicio de sincronización', 'Voltaje estabilizado'],
      },
      mechanical: {
        critical: ['Vibración excesiva', 'Temperatura de caja de cambios crítica'],
        warning: ['Nivel de aceite bajo', 'Desgaste en rodamientos'],
        info: ['Mantenimiento programado', 'Lubricación completada'],
      },
      environmental: {
        critical: ['Viento excede límites operativos'],
        warning: ['Velocidad de viento baja', 'Dirección de viento variable'],
        info: ['Condiciones óptimas de viento'],
      },
      system: {
        critical: ['Pérdida de comunicación'],
        warning: ['Latencia alta en comunicaciones'],
        info: ['Sistema actualizado'],
      },
    };
    
    const typeMessages = messages[type] || messages.system;
    const severityMessages = typeMessages[severity] || typeMessages.info;
    return severityMessages[Math.floor(Math.random() * severityMessages.length)];
  }
}

// Instancia singleton del servicio API
let apiServiceInstance: ApiService | null = null;

export const getApiService = (baseUrl?: string, apiKey?: string): ApiService => {
  if (!apiServiceInstance) {
    apiServiceInstance = new ApiService(baseUrl, apiKey);
  }
  return apiServiceInstance;
};
