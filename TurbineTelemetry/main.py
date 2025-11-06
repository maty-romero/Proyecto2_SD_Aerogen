import time

from TurbineTelemetry.WindTurbine import WindTurbine

if __name__ == "__main__":
    NUM_TURBINES = 50
    turbines = []

    print(f"--- Creando {NUM_TURBINES} turbinas de simulación ---")
    for i in range(1, NUM_TURBINES + 1):
        turbine = WindTurbine(farm_id=1, turbine_id=i)
        turbines.append(turbine)

    print("--- Iniciando todas las turbinas ---")
    for turbine in turbines:
        turbine.start()
    
    print(f"Simulador corriendo con {NUM_TURBINES} turbinas. Presiona Ctrl+C para detener.")
    
    try:
        # Mantener el hilo principal vivo mientras las turbinas publican
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- Deteniendo todas las turbinas ---")
        for turbine in turbines:
            turbine.stop()
        print("--- Todas las turbinas detenidas. Saliendo. ---")