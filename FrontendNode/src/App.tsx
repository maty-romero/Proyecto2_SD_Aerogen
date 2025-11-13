import { useState } from 'react';
import { WindFarmOverview } from './components/WindFarmOverview'; // Este componente será modificado
import { TurbineGrid } from './components/TurbineGrid';
import { ProductionCharts } from './components/ProductionCharts';
import { AlertsPanel } from './components/AlertsPanel';
import { Heatmaps } from './components/Heatmaps';
import { ThemeProvider, useTheme } from './components/ThemeProvider';
import { MqttConnection } from './components/MqttConnection';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { Wind, Sun, Moon } from 'lucide-react';
import { useWindFarmData } from './hooks/useWindFarmData';

// Importamos los componentes que usará WindFarmOverview
import { Card } from './components/ui/card';
import { Gauge, Zap, Activity, ShieldCheck, Wind as WindIcon } from 'lucide-react';

function AppContent() {
  const [selectedTab, setSelectedTab] = useState('overview');
  const { theme, toggleTheme } = useTheme();

  const {
    turbines,
    turbinesList,
    alerts,
    farmStats,
    hourlyProduction,
    weeklyProduction,
    monthlyProduction,
    hourlyWindSpeed,
    hourlyVoltage,
    isConnected,
    loading,
    error,
    lastUpdate,
    connect,
    disconnect,
  } = useWindFarmData({ autoConnect: true });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10 transition-colors">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 dark:bg-blue-500 p-2 rounded-lg">
                <Wind className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-slate-900 dark:text-slate-100">Parque Eólico Comodoro Rivadavia</h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm">Sistema de Monitoreo en Tiempo Real</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <MqttConnection
                isConnected={isConnected}
                onConnect={connect}
                onDisconnect={disconnect}
                error={error}
                lastUpdate={lastUpdate}
              />
              <Button
                variant="outline"
                size="icon"
                onClick={toggleTheme}
                className="rounded-lg"
              >
                {theme === 'light' ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6 space-y-6">
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Vista General</TabsTrigger>
            <TabsTrigger value="turbines">Turbinas</TabsTrigger>
            <TabsTrigger value="analytics">Análisis</TabsTrigger>
            <TabsTrigger value="production">Producción</TabsTrigger>
            <TabsTrigger value="alerts">Panel de Alertas</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <WindFarmOverview farmStats={farmStats} alerts={alerts} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ProductionCharts 
                  hourlyProduction={hourlyProduction}
                  weeklyProduction={weeklyProduction}
                  monthlyProduction={monthlyProduction}
                  hourlyWindSpeed={hourlyWindSpeed}
                  hourlyVoltage={hourlyVoltage}
                  compact 
                />
              </div>
              <div>
                <AlertsPanel alerts={alerts} compact />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="turbines" className="space-y-6">
            <TurbineGrid turbinesList={turbinesList} turbinesMap={turbines} isLoading={loading} />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Heatmaps turbinesList={turbinesList} />
          </TabsContent>

          <TabsContent value="production" className="space-y-6">
            <ProductionCharts 
              hourlyProduction={hourlyProduction}
              weeklyProduction={weeklyProduction}
              monthlyProduction={monthlyProduction}
              hourlyWindSpeed={hourlyWindSpeed}
              hourlyVoltage={hourlyVoltage}
            />
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <AlertsPanel alerts={alerts} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
