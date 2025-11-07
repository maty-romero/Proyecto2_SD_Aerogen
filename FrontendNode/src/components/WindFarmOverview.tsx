import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Wind, Zap, TrendingUp, AlertTriangle, Clock, Activity } from 'lucide-react';
import { Progress } from './ui/progress';

interface WindFarmOverviewProps {
  farmStats: {
    totalPower: number;
    activeTurbines: number;
    totalTurbines: number;
    averagePowerFactor?: number;
    averageWindSpeed?: number;
    averageVoltage?: number;
  } | null;
}

export function WindFarmOverview({ farmStats }: WindFarmOverviewProps) {
  const totalPowerMW = (farmStats?.totalPower || 0) / 1000;
  const totalCapacity = (farmStats?.totalTurbines || 24) * 2.5;
  const activeTurbines = farmStats?.activeTurbines || 0;
  const totalTurbines = farmStats?.totalTurbines || 24;
  const avgPowerFactor = farmStats?.averagePowerFactor || 0;
  const avgWindSpeed = farmStats?.averageWindSpeed || 0;
  const alerts = 0; // This should come from alerts data

  const utilizationRate = (totalPowerMW / totalCapacity) * 100;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Power */}
        <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-slate-500 dark:text-slate-400 text-sm">Potencia Total</p>
              <p className="text-3xl text-slate-900 dark:text-slate-100">{totalPowerMW.toFixed(1)}</p>
              <p className="text-slate-500 dark:text-slate-400 text-sm">MW de {totalCapacity} MW</p>
            </div>
            <div className="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
              <Zap className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <Progress value={utilizationRate} className="mt-4" />
        </Card>

        {/* Active Turbines */}
        <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-slate-500 dark:text-slate-400 text-sm">Turbinas Activas</p>
              <p className="text-3xl text-slate-900 dark:text-slate-100">{activeTurbines}</p>
              <p className="text-slate-500 dark:text-slate-400 text-sm">de {totalTurbines} turbinas</p>
            </div>
            <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
              <Wind className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="mt-4">
            <Badge variant="outline" className="bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">
              {((activeTurbines / totalTurbines) * 100).toFixed(0)}% Operativas
            </Badge>
          </div>
        </Card>

        {/* Power Factor */}
        <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-slate-500 dark:text-slate-400 text-sm">Factor de Potencia</p>
              <p className="text-3xl text-slate-900 dark:text-slate-100">{avgPowerFactor.toFixed(3)}</p>
              <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Óptimo</span>
              </div>
            </div>
            <div className="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </Card>

        {/* Alerts */}
        <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-slate-500 dark:text-slate-400 text-sm">Alertas Activas</p>
              <p className="text-3xl text-slate-900 dark:text-slate-100">{alerts}</p>
              <p className="text-slate-500 dark:text-slate-400 text-sm">Atención requerida</p>
            </div>
            <div className="bg-amber-100 dark:bg-amber-900/30 p-3 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <div className="mt-4">
            {alerts > 0 ? (
              <Badge variant="outline" className="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800">
                Requiere atención
              </Badge>
            ) : (
              <Badge variant="outline" className="bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">
                Todo normal
              </Badge>
            )}
          </div>
        </Card>
      </div>

      {/* Environmental Conditions */}
      <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
        <h3 className="text-slate-900 dark:text-slate-100 mb-4">Condiciones Generales del Parque</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <Wind className="w-4 h-4" /> 
              <span>Velocidad Promedio del Viento</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">{avgWindSpeed.toFixed(1)} m/s</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm">Condiciones óptimas</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <Clock className="w-4 h-4" />
              <span>Última Actualización</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">Ahora</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm">Tiempo real</p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <Activity className="w-4 h-4" />
              <span>Tasa de Utilización</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">{utilizationRate.toFixed(1)}%</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm">Capacidad instalada</p>
          </div>
        </div>
      </Card>

      {/* Electrical Performance */}
      <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
        <h3 className="text-slate-900 dark:text-slate-100 mb-4">Rendimiento Eléctrico del Parque</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <Zap className="w-4 h-4" />
              <span>Potencia Activa Total</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">{(farmStats?.totalPower || 0).toLocaleString()} kW</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm">{totalPowerMW.toFixed(2)} MW</p>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>Producción Estimada Hoy</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">--</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm">MWh generados</p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
              <Activity className="w-4 h-4" />
              <span>Utilización</span>
            </div>
            <p className="text-2xl text-slate-900 dark:text-slate-100">{utilizationRate.toFixed(1)}%</p>
            <Progress value={utilizationRate} className="mt-2" />
          </div>
        </div>
      </Card>
    </div>
  );
}
