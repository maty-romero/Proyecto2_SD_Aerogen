import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { AlertTriangle, Info, Clock, XCircle } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { Alert, AlertSeverity } from '../types/turbine';

const getAlertIcon = (severity: AlertSeverity) => {
  switch (severity) {
    case 'warning':
      return <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />;
    case 'critical':
      return <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />;
    case 'info':
      return <Info className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
    default:
      return <Info className="w-4 h-4 text-slate-600 dark:text-slate-400" />;
  }
};

const getAlertBadge = (severity: AlertSeverity) => {
  switch (severity) {
    case 'warning':
      return <Badge className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800">Advertencia</Badge>;
    case 'critical':
      return <Badge className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800">Crítico</Badge>;
    case 'info':
      return <Badge className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800">Información</Badge>;
    default:
      return <Badge>Desconocido</Badge>;
  }
};

interface AlertsPanelProps {
  alerts: Alert[];
  compact?: boolean;
}

export function AlertsPanel({ alerts, compact = false }: AlertsPanelProps) {
  const activeAlerts = alerts.filter(a => !a.resolvedAt);
  const displayAlerts = compact ? activeAlerts : alerts;

  return (
    <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-900 dark:text-slate-100">
          {compact ? 'Alertas Activas' : 'Panel de Alertas'}
        </h3>
        <Badge variant="outline" className="bg-slate-100 dark:bg-slate-800">
          {activeAlerts.length} activas
        </Badge>
      </div>

      <ScrollArea className={compact ? "h-[400px]" : "h-[600px]"}>
        <div className="space-y-3">
          {displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border transition-colors ${
                !alert.resolvedAt
                  ? 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
                  : 'bg-slate-50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700/50 opacity-60'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 p-2 rounded-lg ${
                  alert.severity === 'warning' ? 'bg-amber-100 dark:bg-amber-900/30' :
                  alert.severity === 'critical' ? 'bg-red-100 dark:bg-red-900/30' :
                  'bg-blue-100 dark:bg-blue-900/30'
                }`}>
                  {getAlertIcon(alert.severity)}
                </div>
                
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-slate-900 dark:text-slate-100 text-sm">{alert.message}</p> 
                      <p className="text-slate-500 dark:text-slate-400 text-xs mt-1">{alert.turbineName}</p>
                    </div>
                    {getAlertBadge(alert.severity)}
                  </div>
                  
                  <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs">
                    <Clock className="w-3 h-3" />
                    <span>{alert.timestamp}</span>
                    {alert.resolvedAt && (
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
