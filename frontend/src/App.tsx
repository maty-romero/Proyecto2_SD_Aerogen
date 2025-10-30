import { useState, useEffect } from 'react';
import { WindFarmOverview } from './components/WindFarmOverview';
import { TurbineGrid } from './components/TurbineGrid';
import { ProductionCharts } from './components/ProductionCharts';
import { AlertsPanel } from './components/AlertsPanel';
import { Heatmaps } from './components/Heatmaps';
import { ThemeProvider, useTheme } from './components/ThemeProvider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { Wind, Sun, Moon, RefreshCw } from 'lucide-react';
import { generateTurbineData } from './utils/turbineData';

function AppContent() {
  const [selectedTab, setSelectedTab] = useState('overview');
  const { theme, toggleTheme } = useTheme();
  const turbines = generateTurbineData();
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [updateText, setUpdateText] = useState<string>('');

  // Simular actualizaciones periódicas
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 5000); // Actualizar cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  // Calcular texto de última actualización
  useEffect(() => {
    const updateTimer = setInterval(() => {
      const now = new Date();
      const diffInSeconds = Math.floor((now.getTime() - lastUpdate.getTime()) / 1000);
      
      if (diffInSeconds < 60) {
        setUpdateText(`hace ${diffInSeconds}s`);
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        setUpdateText(`hace ${minutes}m`);
      } else {
        const hours = Math.floor(diffInSeconds / 3600);
        setUpdateText(`hace ${hours}h`);
      }
    }, 1000);

    return () => clearInterval(updateTimer);
  }, [lastUpdate]);

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
                <h1 className="text-slate-900 dark:text-slate-100">Parque Eólico Valle Verde</h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm">Sistema de Monitoreo en Tiempo Real</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-lg">
                <RefreshCw className="w-4 h-4" />
                <span>Última actualización: {updateText}</span>
              </div>
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
      <main className="container mx-auto px-6 py-6">
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Vista General</TabsTrigger>
            <TabsTrigger value="turbines">Turbinas</TabsTrigger>
            <TabsTrigger value="analytics">Análisis</TabsTrigger>
            <TabsTrigger value="production">Producción</TabsTrigger>
            <TabsTrigger value="alerts">Alertas</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <WindFarmOverview />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ProductionCharts compact />
              </div>
              <div>
                <AlertsPanel compact />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="turbines" className="space-y-6">
            <TurbineGrid />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Heatmaps turbines={turbines} />
          </TabsContent>

          <TabsContent value="production" className="space-y-6">
            <ProductionCharts />
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <AlertsPanel />
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
