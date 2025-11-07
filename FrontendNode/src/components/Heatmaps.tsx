import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Turbine } from '../types/turbine';
import { 
  Zap, 
  TrendingUp, 
  Clock, 
  Wind,
  BarChart3,
  Gauge
} from 'lucide-react';

interface HeatmapsProps {
  turbinesList: Turbine[];
}

// Calcula el color del heatmap basado en un valor normalizado (0-1)
const getHeatColor = (value: number, reverse: boolean = false): string => {
  const normalizedValue = reverse ? 1 - value : value;
  
  if (isNaN(normalizedValue)) return 'bg-slate-200 dark:bg-slate-700';
  if (normalizedValue >= 0.8) return 'bg-green-500 dark:bg-green-600';
  if (normalizedValue >= 0.6) return 'bg-lime-500 dark:bg-lime-600';
  if (normalizedValue >= 0.4) return 'bg-yellow-500 dark:bg-yellow-600';
  if (normalizedValue >= 0.2) return 'bg-orange-500 dark:bg-orange-600';
  return 'bg-red-500 dark:bg-red-600';
};

// Obtiene el color del texto basado en el color de fondo
const getTextColor = (value: number): string => {
  return 'text-white dark:text-white';
};

export function Heatmaps({ turbinesList }: HeatmapsProps) {
  const turbines = turbinesList || [];

  // 1. Heatmap de Generación de Energía
  const maxPower = Math.max(0, ...turbines.map(t => t.electrical.activePower || 0));
  const powerData = turbines.map(t => ({
    id: t.id,
    name: t.name,
    value: t.electrical.activePower,
    normalized: maxPower > 0 ? t.electrical.activePower / maxPower : 0, // Evitar división por cero
    display: `${(t.electrical.activePower / 1000).toFixed(2)} MW`,
  }));

  // 2. Heatmap de Eficiencia Relativa
  const efficiencyData = turbines.map(t => {
    const efficiency = t.status === 'operational' 
      ? (t.electrical.activePower / 1000) / t.capacity 
      : 0;
    return {
      id: t.id,
      name: t.name,
      value: efficiency * 100,
      normalized: efficiency,
      display: `${(efficiency * 100).toFixed(1)}%`,
    };
  });

  // 3. Heatmap de Factor de Potencia
  const powerFactorData = turbines.map(t => ({
    id: t.id,
    name: t.name,
    value: t.electrical.powerFactor,
    normalized: t.electrical.powerFactor,
    display: t.electrical.powerFactor.toFixed(3),
  }));

  // 4. Heatmap de Disponibilidad (simulado basado en status)
  const availabilityData = turbines.map(t => {
    const availability = t.status === 'operational' ? 0.95 + Math.random() * 0.05 :
                        t.status === 'standby' ? 0.7 + Math.random() * 0.2 :
                        t.status === 'maintenance' ? 0.3 + Math.random() * 0.2 :
                        0.1 + Math.random() * 0.2;
    return {
      id: t.id,
      name: t.name,
      value: availability * 100,
      normalized: availability,
      display: `${(availability * 100).toFixed(1)}%`,
    };
  });

  // 5. Heatmap de Velocidad de Viento
  const maxWindSpeed = Math.max(0, ...turbines.map(t => t.environmental.windSpeed || 0));
  const windSpeedData = turbines.map(t => {
    const normalized = maxWindSpeed > 0 ? t.environmental.windSpeed / maxWindSpeed : 0;
    return {
      id: t.id,
      name: t.name,
      value: t.environmental.windSpeed,
      normalized,
      display: `${t.environmental.windSpeed.toFixed(1)} m/s`,
    };
  });

  const renderHeatmap = (
    data: Array<{ id: string; name: string; value: number; normalized: number; display: string }>,
    title: string,
    icon: any,
    reverseColors: boolean = false,
    legendConfig?: {
      minLabel: string;
      maxLabel: string;
      unit?: string;
    }
  ) => {
    const Icon = icon;
    
    // Calcular valores mínimo y máximo para la leyenda
    const minValue = Math.min(...data.map(d => d.value));
    const maxValue = Math.max(...data.map(d => d.value));
    
    // Usar configuración de leyenda personalizada o valores por defecto
    const minLabel = legendConfig?.minLabel || minValue.toFixed(1);
    const maxLabel = legendConfig?.maxLabel || maxValue.toFixed(1);
    const unit = legendConfig?.unit || '';
    
    return (
      <Card className="p-6 dark:bg-slate-800 dark:border-slate-700">
        <div className="flex items-center gap-2 mb-4">
          <Icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="text-slate-900 dark:text-slate-100">{title}</h3>
        </div>
        <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-12 gap-0 border border-slate-200 dark:border-slate-700">
          {data.map((item) => (
            <div
              key={item.id}
              className={`
                aspect-square flex flex-col items-center justify-center
                ${getHeatColor(item.normalized, reverseColors)}
                ${getTextColor(item.normalized)}
                hover:brightness-110 transition-all cursor-pointer
                relative group
                border border-slate-300 dark:border-slate-600
              `}
              title={`${item.name}: ${item.display}`}
            >
              <span className="text-xs opacity-90">
                {item.id.split('-')[1]}
              </span>
              <div className="absolute bottom-full mb-2 hidden group-hover:block z-10">
                <div className="bg-slate-900 dark:bg-slate-700 text-white text-xs rounded px-2 py-1 whitespace-nowrap shadow-lg">
                  {item.name}: {item.display}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* Leyenda mejorada con valores específicos */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-1">
              <div className={`w-6 h-3 rounded ${reverseColors ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <div className="w-6 h-3 rounded bg-orange-500"></div>
              <div className="w-6 h-3 rounded bg-yellow-500"></div>
              <div className="w-6 h-3 rounded bg-lime-500"></div>
              <div className={`w-6 h-3 rounded ${reverseColors ? 'bg-red-500' : 'bg-green-500'}`}></div>
            </div>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span className="font-medium">{minLabel} {unit}</span>
            <span className="font-medium">{maxLabel} {unit}</span>
          </div>
        </div>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        <h2 className="text-slate-900 dark:text-slate-100">Análisis Visual del Parque</h2>
      </div>

      <Tabs defaultValue="power" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="power">Potencia</TabsTrigger>
          <TabsTrigger value="efficiency">Eficiencia</TabsTrigger>
          <TabsTrigger value="operational">Operacionales</TabsTrigger>
        </TabsList>

        <TabsContent value="power" className="space-y-6 mt-6">
          {renderHeatmap(
            powerData, 
            'Generación de Energía por Turbina', 
            Zap,
            false,
            {
              minLabel: '0',
              maxLabel: (maxPower / 1000).toFixed(2),
              unit: 'MW'
            }
          )}
          {renderHeatmap(
            powerFactorData, 
            'Factor de Potencia', 
            TrendingUp,
            false,
            {
              minLabel: '0.90',
              maxLabel: '1.00',
              unit: ''
            }
          )}
        </TabsContent>

        <TabsContent value="efficiency" className="space-y-6 mt-6">
          {renderHeatmap(
            efficiencyData, 
            'Eficiencia Relativa (%)', 
            Gauge,
            false,
            {
              minLabel: '0',
              maxLabel: '100',
              unit: '%'
            }
          )}
          {renderHeatmap(
            availabilityData, 
            'Disponibilidad (%)', 
            Clock,
            false,
            {
              minLabel: '0',
              maxLabel: '100',
              unit: '%'
            }
          )}
        </TabsContent>

        <TabsContent value="operational" className="space-y-6 mt-6">
          {renderHeatmap(
            windSpeedData, 
            'Velocidad del Viento por Turbina', 
            Wind,
            false,
            {
              minLabel: '0',
              maxLabel: maxWindSpeed.toFixed(1),
              unit: 'm/s'
            }
          )}
          
          {/* Heatmap de resumen de estado */}
          <Card className="p-6 dark:bg-slate-800 dark:border-slate-700">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <h3 className="text-slate-900 dark:text-slate-100">Estado de Turbinas</h3>
            </div>
            <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-12 gap-0 border border-slate-200 dark:border-slate-700">
              {turbines.map((turbine) => {
                const statusColors = {
                  operational: 'bg-green-500 dark:bg-green-600',
                  standby: 'bg-blue-500 dark:bg-blue-600',
                  maintenance: 'bg-amber-500 dark:bg-amber-600',
                  fault: 'bg-red-500 dark:bg-red-600',
                  stopped: 'bg-slate-500 dark:bg-slate-600',
                };
                
                const statusLabels = {
                  operational: 'Operativa',
                  standby: 'En Espera',
                  maintenance: 'Mantenimiento',
                  fault: 'Falla',
                  stopped: 'Detenida',
                };
                
                return (
                  <div
                    key={turbine.id}
                    className={`
                      aspect-square flex flex-col items-center justify-center
                      ${statusColors[turbine.status]}
                      text-white
                      hover:brightness-110 transition-all cursor-pointer
                      relative group
                      border border-slate-300 dark:border-slate-600
                    `}
                    title={`${turbine.name}: ${statusLabels[turbine.status]}`}
                  >
                    <span className="text-xs opacity-90">
                      {turbine.id.split('-')[1]}
                    </span>
                    <div className="absolute bottom-full mb-2 hidden group-hover:block z-10">
                      <div className="bg-slate-900 dark:bg-slate-700 text-white text-xs rounded px-2 py-1 whitespace-nowrap shadow-lg">
                        {turbine.name}: {statusLabels[turbine.status]}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Leyenda de estados */}
            <div className="mt-4 flex flex-wrap gap-3 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-green-500"></div>
                <span className="text-slate-600 dark:text-slate-400">Operativa</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-blue-500"></div>
                <span className="text-slate-600 dark:text-slate-400">En Espera</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-amber-500"></div>
                <span className="text-slate-600 dark:text-slate-400">Mantenimiento</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-red-500"></div>
                <span className="text-slate-600 dark:text-slate-400">Falla</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded bg-slate-500"></div>
                <span className="text-slate-600 dark:text-slate-400">Detenida</span>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
