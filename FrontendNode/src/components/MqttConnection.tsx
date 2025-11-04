import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  Settings, 
  Wifi, 
  WifiOff 
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';

interface MqttConnectionProps {
  isConnected: boolean;
  onConnect: (config: MqttConfig) => void;
  onDisconnect: () => void;
  error?: string | null;
  lastUpdate?: Date | null;
}

interface MqttConfig {
  brokerUrl: string;
  username?: string;
  password?: string;
}

export function MqttConnection({ 
  isConnected, 
  onConnect, 
  onDisconnect, 
  error,
  lastUpdate 
}: MqttConnectionProps) {
  const [open, setOpen] = useState(false);
  const [config, setConfig] = useState<MqttConfig>({
    brokerUrl: 'ws://localhost:8083/mqtt',
    username: '',
    password: '',
  });

  const handleConnect = () => {
    onConnect(config);
    setOpen(false);
  };

  const formatLastUpdate = (date: Date | null | undefined) => {
    if (!date) return 'Nunca';
    
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return `Hace ${seconds}s`;
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    return `Hace ${Math.floor(seconds / 3600)}h`;
  };

  return (
    <Card className="p-4 dark:bg-slate-900 dark:border-slate-800">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isConnected ? 'bg-green-100 dark:bg-green-900/30' : 'bg-slate-100 dark:bg-slate-800'}`}>
            {isConnected ? (
              <Wifi className="w-5 h-5 text-green-600 dark:text-green-400" />
            ) : (
              <WifiOff className="w-5 h-5 text-slate-500 dark:text-slate-400" />
            )}
          </div>
          
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-slate-900 dark:text-slate-100">Conexión MQTT</h3>
              {isConnected ? (
                <Badge className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Conectado
                </Badge>
              ) : (
                <Badge variant="outline" className="text-slate-600 dark:text-slate-400">
                  Desconectado
                </Badge>
              )}
            </div>
            
            {isConnected && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                <Activity className="w-3 h-3 inline mr-1" />
                Última actualización: {formatLastUpdate(lastUpdate)}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Configurar
              </Button>
            </DialogTrigger>
            <DialogContent className="dark:bg-slate-900">
              <DialogHeader>
                <DialogTitle className="dark:text-slate-100">Configuración MQTT</DialogTitle>
                <DialogDescription className="dark:text-slate-400">
                  Configure la conexión al broker EMQX
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="brokerUrl" className="dark:text-slate-200">URL del Broker</Label>
                  <Input
                    id="brokerUrl"
                    placeholder="ws://localhost:8083/mqtt"
                    value={config.brokerUrl}
                    onChange={(e) => setConfig({ ...config, brokerUrl: e.target.value })}
                    className="dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100"
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Ejemplo: ws://localhost:8083/mqtt o wss://broker.emqx.io:8084/mqtt
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="username" className="dark:text-slate-200">Usuario (opcional)</Label>
                  <Input
                    id="username"
                    placeholder="Usuario MQTT"
                    value={config.username}
                    onChange={(e) => setConfig({ ...config, username: e.target.value })}
                    className="dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="dark:text-slate-200">Contraseña (opcional)</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Contraseña MQTT"
                    value={config.password}
                    onChange={(e) => setConfig({ ...config, password: e.target.value })}
                    className="dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100"
                  />
                </div>

                <Alert className="dark:bg-blue-900/20 dark:border-blue-800">
                  <AlertCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <AlertDescription className="text-sm text-blue-800 dark:text-blue-300">
                    Tópicos esperados (JSON plano):
                    <ul className="list-disc list-inside mt-2 space-y-1 text-xs">
                      <li>windfarm/turbines/+/measurements</li>
                      <li>windfarm/alerts</li>
                      <li>windfarm/stats</li>
                    </ul>
                  </AlertDescription>
                </Alert>

                <div className="flex justify-end gap-2 mt-6">
                  <Button 
                    variant="outline" 
                    onClick={() => setOpen(false)}
                    className="dark:border-slate-700"
                  >
                    Cancelar
                  </Button>
                  <Button onClick={handleConnect}>
                    Conectar
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          {isConnected ? (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onDisconnect}
              className="text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              Desconectar
            </Button>
          ) : null}
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </Card>
  );
}
