import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { WindRose } from './WindRose';
import { 
  Wind, 
  Zap, 
  Activity, 
  Gauge, 
  Thermometer,
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Droplet,
  Compass,
  RotateCw,
  Settings,
  Pause
} from 'lucide-react';
import { Card } from './ui/card';
import { Separator } from './ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Turbine } from '../types/turbine';
import { getStatusLabel, getStatusColor } from '../utils/turbineData';

interface TurbineDetailDialogProps {
  turbineId: string | null;
  turbinesMap: Map<string, Turbine>;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

// Mock historical data for the turbine
const generateHistoricalData = () => {
  // NOTA: Esto debería ser reemplazado por datos reales de la API en el futuro.
  return Array.from({ length: 24 }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    power: 1500 + Math.random() * 1000,
    windSpeed: 8 + Math.random() * 6,
    temperature: 50 + Math.random() * 15,
  }));
};

const getStatusBadge = (status: Turbine['status']) => {
  const colors = getStatusColor(status);
  const icons = {
    operational: CheckCircle,
    maintenance: AlertTriangle,
    fault: XCircle,
    stopped: Pause,
    standby: Clock,
  };
  const Icon = icons[status];
  
  return (
    <Badge className={`${colors.bg} ${colors.text} ${colors.border}`}>
      <Icon className="w-3 h-3 mr-1" />
      {getStatusLabel(status)}
    </Badge>
  );
};

export function TurbineDetailDialog({ turbineId, turbinesMap, open, onOpenChange }: TurbineDetailDialogProps) {
  const turbine = turbineId ? turbinesMap.get(turbineId) : null;

  if (!turbine || !turbineId) return null;

  const historicalData = generateHistoricalData();
  const powerMW = turbine.electrical.activePower / 1000;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto dark:bg-slate-900">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="dark:text-slate-100">{turbine.name}</DialogTitle>
              <DialogDescription className="text-slate-500 dark:text-slate-400 text-sm mt-1">
                {turbine.id} - Capacidad: {turbine.capacity} MW
              </DialogDescription>
            </div>
            {getStatusBadge(turbine.status)}
          </div>
        </DialogHeader>

        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">General</TabsTrigger>
            <TabsTrigger value="mechanical">Mecánicas</TabsTrigger>
            <TabsTrigger value="electrical">Eléctricas</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Power Output */}
            <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h3 className="text-slate-900 dark:text-slate-100">Potencia Actual</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl text-slate-900 dark:text-slate-100">{powerMW.toFixed(2)}</span>
                  <span className="text-slate-500 dark:text-slate-400">MW de {turbine.capacity} MW</span>
                </div>
                <Progress value={(powerMW / turbine.capacity) * 100} />
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm">
                  <TrendingUp className="w-4 h-4" />
                  <span>Operando a {((powerMW / turbine.capacity) * 100).toFixed(1)}% de capacidad</span>
                </div>
              </div>
            </Card>

            {/* Wind Rose */}
            <Card className="p-6 dark:bg-slate-800 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-4">
                <Wind className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h3 className="text-slate-900 dark:text-slate-100">Dirección y Velocidad del Viento</h3>
              </div>
              <WindRose 
                direction={turbine.environmental.windDirection} 
                speed={turbine.environmental.windSpeed} 
              />
            </Card>

            {/* Performance Chart */}
            <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
              <h3 className="text-slate-900 dark:text-slate-100 mb-4">Rendimiento (24h)</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                    interval={5}
                  />
                  <YAxis 
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="power" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Potencia (kW)"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Maintenance Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-2">
                  <Calendar className="w-4 h-4" />
                  <span>Último Mantenimiento</span>
                </div>
                <p className="text-slate-900 dark:text-slate-100">{turbine.lastMaintenance}</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-2">
                  <Clock className="w-4 h-4" />
                  <span>Próximo Mantenimiento</span>
                </div>
                <p className="text-slate-900 dark:text-slate-100">{turbine.nextMaintenance}</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-2">
                  <Activity className="w-4 h-4" />
                  <span>Horas de Operación</span>
                </div>
                <p className="text-slate-900 dark:text-slate-100">{turbine.operatingHours.toLocaleString()} h</p>
              </Card>
            </div>
          </TabsContent>

          {/* Mechanical Tab */}
          <TabsContent value="mechanical" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <RotateCw className="w-4 h-4" />
                  <span>Velocidad del Rotor</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.rotorSpeed.toFixed(1)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">RPM</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Settings className="w-4 h-4" />
                  <span>Ángulo de Pitch</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.pitchAngle.toFixed(1)}°</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">grados</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Compass className="w-4 h-4" />
                  <span>Posición Yaw</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.yawPosition}°</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">grados</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Gauge className="w-4 h-4" />
                  <span>Vibraciones</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.vibration.toFixed(2)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">mm/s</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Thermometer className="w-4 h-4" />
                  <span>Temp. Engranaje</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.gearboxTemperature.toFixed(1)}°C</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Celsius</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Thermometer className="w-4 h-4" />
                  <span>Temp. Rodamientos</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.bearingTemperature.toFixed(1)}°C</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Celsius</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Droplet className="w-4 h-4" />
                  <span>Presión del Aceite</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.oilPressure.toFixed(2)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">bar</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Droplet className="w-4 h-4" />
                  <span>Nivel de Aceite</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.mechanical.oilLevel.toFixed(1)}%</p>
                <Progress value={turbine.mechanical.oilLevel} className="mt-2" />
              </Card>
            </div>
          </TabsContent>

          {/* Electrical Tab */}
          <TabsContent value="electrical" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Zap className="w-4 h-4" />
                  <span>Voltaje de Salida</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.electrical.outputVoltage.toFixed(1)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">V</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Activity className="w-4 h-4" />
                  <span>Corriente Generada</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.electrical.outputCurrent.toFixed(1)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">A</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Zap className="w-4 h-4" />
                  <span>Potencia Activa</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.electrical.activePower.toFixed(0)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">kW</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <Zap className="w-4 h-4" />
                  <span>Potencia Reactiva</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.electrical.reactivePower.toFixed(0)}</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">kVAR</p>
              </Card>

              <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm mb-3">
                  <TrendingUp className="w-4 h-4" />
                  <span>Factor de Potencia</span>
                </div>
                <p className="text-3xl text-slate-900 dark:text-slate-100">{turbine.electrical.powerFactor.toFixed(3)}</p>
                <Progress value={turbine.electrical.powerFactor * 100} className="mt-2" />
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
