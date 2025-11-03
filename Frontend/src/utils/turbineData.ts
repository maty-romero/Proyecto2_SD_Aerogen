import { Turbine, TurbineStatus } from '../types/turbine';

export const generateTurbineData = (): Turbine[] => {
  const turbines: Turbine[] = [];
  
  for (let i = 1; i <= 24; i++) {
    const random = Math.random();
    let status: TurbineStatus = 'operational';
    
    if (i === 7 || i === 15) {
      status = 'maintenance';
    } else if (i === 3) {
      status = 'standby';
    } else if (random > 0.97) {
      status = 'fault';
    } else if (random > 0.95) {
      status = 'stopped';
    }
    
    const isActive = status === 'operational';
    const windSpeed = 8 + Math.random() * 10;
    const activePower = isActive ? (windSpeed / 18) * 2.5 * (0.7 + Math.random() * 0.3) : 0;
    
    turbines.push({
      id: `WT-${String(i).padStart(3, '0')}`,
      name: `Turbina ${i}`,
      status,
      capacity: 2.5, // MW
      
      environmental: {
        windSpeed,
        windDirection: Math.floor(Math.random() * 360),
      },
      
      mechanical: {
        rotorSpeed: isActive ? 10 + Math.random() * 8 : 0,
        pitchAngle: isActive ? 5 + Math.random() * 10 : 90,
        yawPosition: Math.floor(Math.random() * 360),
        vibration: isActive ? 0.5 + Math.random() * 1.5 : 0,
        gearboxTemperature: isActive ? 50 + Math.random() * 20 : 25,
        bearingTemperature: isActive ? 45 + Math.random() * 15 : 25,
        oilPressure: isActive ? 2.5 + Math.random() * 1.5 : 0,
        oilLevel: 80 + Math.random() * 15,
      },
      
      electrical: {
        outputVoltage: isActive ? 690 + Math.random() * 10 : 0,
        outputCurrent: isActive ? activePower * 1000 / (690 * Math.sqrt(3) * 0.95) : 0,
        activePower: activePower * 1000, // Convert to kW
        reactivePower: isActive ? activePower * 1000 * 0.3 : 0,
        powerFactor: isActive ? 0.92 + Math.random() * 0.06 : 0,
      },
      
      lastMaintenance: '2025-09-15',
      nextMaintenance: '2025-12-15',
      operatingHours: 12500 + Math.floor(Math.random() * 2000),
    });
  }
  
  return turbines;
};

export const getStatusLabel = (status: TurbineStatus): string => {
  const labels: Record<TurbineStatus, string> = {
    operational: 'Operativa',
    stopped: 'Detenida',
    fault: 'Falla',
    maintenance: 'Mantenimiento',
    standby: 'En Espera',
  };
  return labels[status];
};

export const getStatusColor = (status: TurbineStatus) => {
  switch (status) {
    case 'operational':
      return {
        bg: 'bg-green-100 dark:bg-green-900/30',
        text: 'text-green-700 dark:text-green-400',
        border: 'border-green-200 dark:border-green-800',
        hover: 'hover:border-green-300 dark:hover:border-green-700 hover:bg-green-50/50 dark:hover:bg-green-900/20',
      };
    case 'maintenance':
      return {
        bg: 'bg-amber-100 dark:bg-amber-900/30',
        text: 'text-amber-700 dark:text-amber-400',
        border: 'border-amber-200 dark:border-amber-800',
        hover: 'hover:border-amber-300 dark:hover:border-amber-700 hover:bg-amber-50/50 dark:hover:bg-amber-900/20',
      };
    case 'fault':
      return {
        bg: 'bg-red-100 dark:bg-red-900/30',
        text: 'text-red-700 dark:text-red-400',
        border: 'border-red-200 dark:border-red-800',
        hover: 'hover:border-red-300 dark:hover:border-red-700 hover:bg-red-50/50 dark:hover:bg-red-900/20',
      };
    case 'stopped':
      return {
        bg: 'bg-slate-100 dark:bg-slate-800/30',
        text: 'text-slate-700 dark:text-slate-400',
        border: 'border-slate-200 dark:border-slate-700',
        hover: 'hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50/50 dark:hover:bg-slate-800/20',
      };
    case 'standby':
      return {
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-700 dark:text-blue-400',
        border: 'border-blue-200 dark:border-blue-800',
        hover: 'hover:border-blue-300 dark:hover:border-blue-700 hover:bg-blue-50/50 dark:hover:bg-blue-900/20',
      };
  }
};
