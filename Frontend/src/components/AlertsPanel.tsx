import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { AlertTriangle, Info, CheckCircle, Clock, XCircle } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';

// Mock alerts data with more technical details
const alerts = [
  {
    id: 1,
    type: 'warning',
    turbine: 'WT-007',
    message: 'Mantenimiento preventivo programado',
    details: 'Revisión de sistema hidráulico de pitch',
    timestamp: '2025-10-28 08:30',
    status: 'pending',
  },
  {
    id: 2,
    type: 'warning',
    turbine: 'WT-015',
    message: 'Temperatura del engranaje elevada',
    details: 'Temp. actual: 72°C (límite: 70°C)',
    timestamp: '2025-10-28 09:15',
    status: 'pending',
  },
  {
    id: 3,
    type: 'error',
    turbine: 'WT-003',
    message: 'Vibración excesiva detectada',
    details: 'Vibración: 3.2 mm/s (límite: 2.5 mm/s)',
    timestamp: '2025-10-28 10:05',
    status: 'pending',
  },
  {
    id: 4,
    type: 'info',
    turbine: 'General',
    message: 'Actualización del sistema SCADA completada',
    details: 'Versión 2.4.1 instalada exitosamente',
    timestamp: '2025-10-28 06:00',
    status: 'resolved',
  },
  {
    id: 5,
    type: 'success',
    turbine: 'WT-012',
    message: 'Calibración de sensores completada',
    details: 'Anemómetro y veleta recalibrados',
    timestamp: '2025-10-27 16:45',
    status: 'resolved',
  },
  {
    id: 6,
    type: 'info',
    turbine: 'WT-019',
    message: 'Nivel de aceite bajo',
    details: 'Nivel actual: 78% (recomendado: >85%)',
    timestamp: '2025-10-27 14:20',
    status: 'pending',
  },
];

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'warning':
      return <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />;
    case 'error':
      return <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />;
    case 'info':
      return <Info className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
    case 'success':
      return <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />;
    default:
      return <Info className="w-4 h-4 text-slate-600 dark:text-slate-400" />;
  }
};

const getAlertBadge = (type: string) => {
  switch (type) {
    case 'warning':
      return <Badge className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800">Advertencia</Badge>;
    case 'error':
      return <Badge className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800">Error</Badge>;
    case 'info':
      return <Badge className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800">Información</Badge>;
    case 'success':
      return <Badge className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">Completado</Badge>;
    default:
      return <Badge>Desconocido</Badge>;
  }
};

interface AlertsPanelProps {
  compact?: boolean;
}

export function AlertsPanel({ compact = false }: AlertsPanelProps) {
  const displayAlerts = compact ? alerts.filter(a => a.status === 'pending') : alerts;

  return (
    <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-900 dark:text-slate-100">
          {compact ? 'Alertas Activas' : 'Panel de Alertas'}
        </h3>
        <Badge variant="outline" className="bg-slate-100 dark:bg-slate-800">
          {alerts.filter(a => a.status === 'pending').length} activas
        </Badge>
      </div>

      <ScrollArea className={compact ? "h-[400px]" : "h-[600px]"}>
        <div className="space-y-3">
          {displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border transition-colors ${
                alert.status === 'pending'
                  ? 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
                  : 'bg-slate-50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700/50 opacity-60'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 p-2 rounded-lg ${
                  alert.type === 'warning' ? 'bg-amber-100 dark:bg-amber-900/30' :
                  alert.type === 'error' ? 'bg-red-100 dark:bg-red-900/30' :
                  alert.type === 'info' ? 'bg-blue-100 dark:bg-blue-900/30' : 
                  'bg-green-100 dark:bg-green-900/30'
                }`}>
                  {getAlertIcon(alert.type)}
                </div>
                
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-slate-900 dark:text-slate-100 text-sm">{alert.message}</p>
                      <p className="text-slate-500 dark:text-slate-400 text-xs mt-1">{alert.turbine}</p>
                      {alert.details && (
                        <p className="text-slate-600 dark:text-slate-300 text-xs mt-1 italic">{alert.details}</p>
                      )}
                    </div>
                    {getAlertBadge(alert.type)}
                  </div>
                  
                  <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs">
                    <Clock className="w-3 h-3" />
                    <span>{alert.timestamp}</span>
                    {alert.status === 'resolved' && (
                      <Badge variant="outline" className="ml-auto bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800 text-xs">
                        Resuelto
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}
