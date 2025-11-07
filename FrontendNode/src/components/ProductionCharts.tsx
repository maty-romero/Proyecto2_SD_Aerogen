import { Card } from './ui/card';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data for charts
const weeklyData = [
  { day: 'Lun', production: 1150, target: 1200, activePower: 48500 },
  { day: 'Mar', production: 1280, target: 1200, activePower: 53300 },
  { day: 'Mié', production: 980, target: 1200, activePower: 40800 },
  { day: 'Jue', production: 1420, target: 1200, activePower: 59200 },
  { day: 'Vie', production: 1350, target: 1200, activePower: 56300 },
  { day: 'Sáb', production: 1180, target: 1200, activePower: 49200 },
  { day: 'Dom', production: 1050, target: 1200, activePower: 43800 },
];

const monthlyData = [
  { month: 'Ene', production: 32400, powerFactor: 0.94 },
  { month: 'Feb', production: 29800, powerFactor: 0.92 },
  { month: 'Mar', production: 35200, powerFactor: 0.96 },
  { month: 'Abr', production: 34100, powerFactor: 0.95 },
  { month: 'May', production: 36800, powerFactor: 0.97 },
  { month: 'Jun', production: 33500, powerFactor: 0.94 },
  { month: 'Jul', production: 31200, powerFactor: 0.93 },
  { month: 'Ago', production: 33900, powerFactor: 0.95 },
  { month: 'Sep', production: 35600, powerFactor: 0.96 },
  { month: 'Oct', production: 37200, powerFactor: 0.97 },
];

interface ProductionChartsProps {
  hourlyProduction: { hour: string; power: number }[];
  compact?: boolean;
}

export function ProductionCharts({ hourlyProduction, compact = false }: ProductionChartsProps) {
  return (
    <div className="space-y-6">
      {/* Real-time Power Output */}
      <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
        <h3 className="text-slate-900 dark:text-slate-100 mb-4">Potencia Activa en Tiempo Real (24h)</h3>
        <ResponsiveContainer width="100%" height={compact ? 250 : 350}>
          <AreaChart data={hourlyProduction}>
            <defs>
              <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
            <XAxis 
              dataKey="hour" 
              className="text-slate-600 dark:text-slate-400"
              tick={{ fontSize: 12 }}
              interval={compact ? 5 : 2}
            />
            <YAxis 
              className="text-slate-600 dark:text-slate-400"
              tick={{ fontSize: 12 }}
              label={{ value: 'kW', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1e293b', 
                border: 'none', 
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="power" 
              stroke="#3b82f6" 
              strokeWidth={2}
              fill="url(#colorPower)"
              name="Potencia (kW)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {!compact && (
        <>
          {/* Weekly Production */}
          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h3 className="text-slate-900 dark:text-slate-100 mb-4">Producción Semanal</h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis 
                  dataKey="day" 
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'MWh', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: 'none', 
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                <Bar dataKey="production" fill="#10b981" name="Producción Real" radius={[8, 8, 0, 0]} />
                <Bar dataKey="target" fill="#64748b" name="Objetivo" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Wind Speed Trends */}
          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h3 className="text-slate-900 dark:text-slate-100 mb-4">Velocidad del Viento y Voltaje (24h)</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={hourlyProduction}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis 
                  dataKey="hour" 
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  interval={2}
                />
                <YAxis 
                  yAxisId="left"
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'm/s', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
                />
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'V', angle: 90, position: 'insideRight', style: { fontSize: 12 } }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: 'none', 
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="windSpeed" 
                  stroke="#06b6d4" 
                  strokeWidth={2}
                  name="Velocidad Viento (m/s)"
                  dot={{ r: 3 }}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="voltage" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  name="Voltaje (V)"
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Monthly Trends */}
          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h3 className="text-slate-900 dark:text-slate-100 mb-4">Tendencias Mensuales</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
                <XAxis 
                  dataKey="month" 
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  yAxisId="left"
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'MWh', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
                />
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  className="text-slate-600 dark:text-slate-400"
                  tick={{ fontSize: 12 }}
                  domain={[0.9, 1]}
                  label={{ value: 'Factor Potencia', angle: 90, position: 'insideRight', style: { fontSize: 12 } }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: 'none', 
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="production" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Producción (MWh)"
                  dot={{ r: 4 }}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="powerFactor" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  name="Factor de Potencia"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
    </div>
  );
}
