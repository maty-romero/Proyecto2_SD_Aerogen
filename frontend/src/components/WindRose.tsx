interface WindRoseProps {
  direction: number; // 0-360 degrees
  speed: number;
}

export function WindRose({ direction, speed }: WindRoseProps) {
  const getDirectionLabel = (deg: number) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'];
    const index = Math.round(deg / 45) % 8;
    return directions[index];
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-64 h-64">
        {/* Background circle */}
        <svg className="w-full h-full" viewBox="0 0 200 200">
          {/* Outer circles */}
          <circle cx="100" cy="100" r="90" fill="none" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          <circle cx="100" cy="100" r="70" fill="none" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          <circle cx="100" cy="100" r="50" fill="none" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          <circle cx="100" cy="100" r="30" fill="none" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          
          {/* Cardinal direction lines */}
          <line x1="100" y1="10" x2="100" y2="190" stroke="currentColor" strokeWidth="1" className="text-slate-300 dark:text-slate-600" />
          <line x1="10" y1="100" x2="190" y2="100" stroke="currentColor" strokeWidth="1" className="text-slate-300 dark:text-slate-600" />
          <line x1="27" y1="27" x2="173" y2="173" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          <line x1="173" y1="27" x2="27" y2="173" stroke="currentColor" strokeWidth="1" className="text-slate-200 dark:text-slate-700" />
          
          {/* Direction labels */}
          <text x="100" y="20" textAnchor="middle" className="fill-slate-700 dark:fill-slate-300 text-sm">N</text>
          <text x="180" y="105" textAnchor="middle" className="fill-slate-700 dark:fill-slate-300 text-sm">E</text>
          <text x="100" y="195" textAnchor="middle" className="fill-slate-700 dark:fill-slate-300 text-sm">S</text>
          <text x="20" y="105" textAnchor="middle" className="fill-slate-700 dark:fill-slate-300 text-sm">O</text>
          
          {/* Wind direction arrow - centered triangle with smooth rotation */}
          <g 
            transform={`rotate(${direction}, 100, 100)`}
            style={{
              transition: 'transform 0.5s ease-out',
              transformOrigin: '100px 100px'
            }}
          >
            {/* Triangular arrow centered and pointing outward */}
            <polygon 
              points="100,30 92,110 108,110" 
              fill="currentColor"
              className="text-blue-600 dark:text-blue-400"
              style={{ opacity: 0.9 }}
            />
          </g>
          
          {/* Center dot */}
          <circle cx="100" cy="100" r="4" fill="currentColor" className="text-slate-900 dark:text-slate-100" />
        </svg>
      </div>
      
      {/* Speed and direction info below the rose */}
      <div className="flex gap-6 items-center">
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm px-4 py-2 border border-slate-200 dark:border-slate-700">
          <p className="text-slate-500 dark:text-slate-400 text-xs">Dirección</p>
          <p className="text-slate-900 dark:text-slate-100 text-center">{getDirectionLabel(direction)} ({direction}°)</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm px-4 py-2 border border-slate-200 dark:border-slate-700">
          <p className="text-slate-500 dark:text-slate-400 text-xs">Velocidad</p>
          <p className="text-blue-600 dark:text-blue-400 text-center">{speed.toFixed(1)} m/s</p>
        </div>
      </div>
    </div>
  );
}
