import { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Wind, AlertTriangle, CheckCircle, XCircle, Pause, Clock } from 'lucide-react';
import { TurbineDetailDialog } from './TurbineDetailDialog';
import { getStatusColor } from '../utils/turbineData';
import { Turbine } from '../types/turbine';

interface TurbineGridProps {
  turbinesList: Turbine[];
  turbinesMap: Map<string, Turbine>;
  isLoading: boolean;
}
const getStatusIcon = (status: Turbine['status']) => {
  const iconClass = "w-3 h-3";
  switch (status) {
    case 'operational':
      return <CheckCircle className={`${iconClass} text-green-600 dark:text-green-400`} />;
    case 'maintenance':
      return <AlertTriangle className={`${iconClass} text-amber-600 dark:text-amber-400`} />;
    case 'fault':
      return <XCircle className={`${iconClass} text-red-600 dark:text-red-400`} />;
    case 'stopped':
      return <Pause className={`${iconClass} text-slate-600 dark:text-slate-400`} />;
    case 'standby':
      return <Clock className={`${iconClass} text-blue-600 dark:text-blue-400`} />;
  }
};

export function TurbineGrid({ turbinesList, turbinesMap, isLoading }: TurbineGridProps) {
  const [selectedTurbineId, setSelectedTurbineId] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleTurbineClick = (turbine: Turbine) => {
    setSelectedTurbineId(turbine.id);
    setDialogOpen(true);
  };

  const statusCounts = (turbinesList || []).reduce((acc, turbine) => {
    acc[turbine.status] = (acc[turbine.status] || 0) + 1;
    return acc;
  }, {} as Record<Turbine['status'], number>);
  
  if (isLoading && (!turbinesList || turbinesList.length === 0)) {
    return <div>Cargando turbinas...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-slate-900 dark:text-slate-100">Estado de Turbinas</h2>
          <p className="text-slate-500 dark:text-slate-400">Haz clic en una turbina para ver detalles completos</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {statusCounts.operational && (
            <Badge className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">
              {statusCounts.operational} Operativas
            </Badge>
          )}
          {statusCounts.maintenance && (
            <Badge className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800">
              {statusCounts.maintenance} Mantenimiento
            </Badge>
          )}
          {statusCounts.fault && (
            <Badge className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800">
              {statusCounts.fault} Fallas
            </Badge>
          )}
        </div>
      </div>

      {/* Compact Grid View */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
        {(turbinesList || []).map((turbine) => {
          const colors = getStatusColor(turbine.status);
          const powerMW = turbine.electrical.activePower / 1000;
          
          return (
            <Card 
              key={turbine.id} 
              className={`p-3 cursor-pointer transition-all border-2 ${colors.border} ${colors.hover} dark:bg-slate-900`}
              onClick={() => handleTurbineClick(turbine)}
            >
              <div className="space-y-2">
                {/* Header with icon */ }
                <div className="flex items-center justify-between">
                  <span className="text-slate-900 dark:text-slate-100 text-sm">{turbine.id}</span>
                  {getStatusIcon(turbine.status)}
                </div>

                {/* Power indicator */}
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Potencia</p>
                  <p className="text-slate-900 dark:text-slate-100">{powerMW.toFixed(2)} MW</p>
                </div>

                {/* Mini progress bar */}
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full transition-all ${
                      turbine.status === 'operational' ? 'bg-green-500 dark:bg-green-400' :
                      turbine.status === 'maintenance' ? 'bg-amber-500 dark:bg-amber-400' :
                      turbine.status === 'fault' ? 'bg-red-500 dark:bg-red-400' :
                      turbine.status === 'standby' ? 'bg-blue-500 dark:bg-blue-400' :
                      'bg-slate-400 dark:bg-slate-500'
                    }`}
                    style={{ width: `${(powerMW / turbine.capacity) * 100}%` }}
                  />
                </div>

                {/* Quick metrics */}
                <div className="grid grid-cols-2 gap-1 text-xs">
                  <div>
                    <p className="text-slate-400 dark:text-slate-500">Viento</p>
                    <p className="text-slate-700 dark:text-slate-300">{turbine.environmental.windSpeed.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 dark:text-slate-500">RPM</p>
                    <p className="text-slate-700 dark:text-slate-300">{turbine.mechanical.rotorSpeed.toFixed(1)}</p>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Detail Dialog */}
      <TurbineDetailDialog 
        turbineId={selectedTurbineId}
        turbinesMap={turbinesMap}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </div>
  );
}
