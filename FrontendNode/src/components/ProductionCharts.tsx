import { Card } from './ui/card';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ProductionChartsProps {
  hourlyProduction: { hour: string; power: number }[];
  weeklyProduction: { day: string; production: number }[];
  monthlyProduction: { month: string; production: number }[];
  hourlyWindSpeed: { hour: string; windSpeed: number }[];
  hourlyVoltage: { hour: string; voltage: number }[];
  compact?: boolean;
}

export function ProductionCharts({
  hourlyProduction,
  weeklyProduction,
  monthlyProduction,
  hourlyWindSpeed,
  hourlyVoltage,
  compact = false
}: ProductionChartsProps) {

  // Combinar datos horarios para el gráfico de viento y voltaje
  const combinedHourlyData = hourlyProduction.map((prod, index) => ({
    ...prod,
    windSpeed: hourlyWindSpeed[index]?.windSpeed || 0,
    voltage: hourlyVoltage[index]?.voltage || 0,
  }));

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
              <BarChart data={weeklyProduction}>
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
                <Bar dataKey="production" fill="#10b981" name="Producción (MWh)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Wind Speed Trends */}
          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h3 className="text-slate-900 dark:text-slate-100 mb-4">Velocidad del Viento y Voltaje (24h)</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={combinedHourlyData}>
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
              <LineChart data={monthlyProduction}>
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
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
    </div>
  );
}

