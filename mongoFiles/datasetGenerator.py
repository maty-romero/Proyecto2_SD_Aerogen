import json
import random
import time
from datetime import datetime, timedelta, timezone
import os
from bson import json_util

# --- Configuration ---
NUM_FARMS = 1
TURBINES_PER_FARM = 25
START_DATE = datetime(2024, 11, 15, tzinfo=timezone.utc)  # Fecha actual con timezone UTC
END_DATE = START_DATE + timedelta(days=365)  # Solo 1 día de datos para pruebas
TIME_INTERVAL_MINUTES = 20  # Cada 20 minutos (más datos por hora)
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.json")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator_state.json")

# --- Power Curve Simulation ---
CUT_IN_SPEED = 3.5  # m/s
RATED_SPEED = 14  # m/s
CUT_OUT_SPEED = 25  # m/s
MAX_POWER_KW = 2500  # 2.5 MW
CAPACITY_MW = 2.5

def get_active_power(wind_speed):
    """Calculates active power based on a simplified wind turbine power curve."""
    if wind_speed < CUT_IN_SPEED or wind_speed > CUT_OUT_SPEED:
        return 0.0
    if wind_speed < RATED_SPEED:
        # Power increases cubically with wind speed
        return round((MAX_POWER_KW * ((wind_speed - CUT_IN_SPEED) / (RATED_SPEED - CUT_IN_SPEED))**3), 2)
    return round(MAX_POWER_KW, 2)

def generate_turbine_data(farm_id, turbine_id, timestamp):
    """Generates a single realistic data point for a wind turbine."""
    wind_speed = round(random.uniform(0, CUT_OUT_SPEED + 5), 2)
    active_power = get_active_power(wind_speed)

    # Aumentar probabilidad de operación al 95%
    is_operational = active_power > 0 and random.random() > 0.05
    
    if is_operational:
        operational_state = "operational"
    else:
        operational_state = random.choice(["stopped", "fault", "maintenance", "standby"])

    if not is_operational:
        active_power = 0

    rotor_speed = round((wind_speed / RATED_SPEED) * 20, 2) if is_operational and wind_speed > 0 else 0
    blade_pitch = round((wind_speed / RATED_SPEED) * 15, 2) if is_operational else 90  # 90° cuando está parado
    
    # Calcular voltage y current solo si está operacional
    output_voltage = round(400 + random.uniform(-10, 10), 2) if is_operational else 0
    generated_current = round((active_power * 1000) / (output_voltage * 1.732), 2) if is_operational and output_voltage > 0 else 0

    data = {
        "farm_id": farm_id,
        "farm_name": f"Farm-{farm_id:003d}",
        "turbine_id": turbine_id,
        "turbine_name": f"T-{turbine_id:003d}",
        # ✅ CAMBIO PRINCIPAL: timestamp como datetime object (UTC)
        "timestamp": timestamp,  # Ya es datetime con timezone UTC
        "timestamp_str": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "capacity_mw": CAPACITY_MW,
        "operational_state": operational_state,
        "active_power_kw": active_power,
        "reactive_power_kvar": round(active_power * 0.33, 2),  # Factor de potencia ~0.95
        "generated_current_a": generated_current,
        "output_voltage_v": output_voltage,
        "wind_speed_mps": wind_speed,
        "wind_direction_deg": random.randint(0, 359),
        "yaw_position_deg": random.randint(0, 359),
        "rotor_speed_rpm": rotor_speed,
        "blade_pitch_angle_deg": blade_pitch,
        "gear_temperature_c": round(40 + (active_power / MAX_POWER_KW) * 40 + random.uniform(-2, 2), 1) if is_operational else round(random.uniform(20, 30), 1),
        "bearing_temperature_c": round(35 + (active_power / MAX_POWER_KW) * 35 + random.uniform(-2, 2), 1) if is_operational else round(random.uniform(20, 30), 1),
        "vibrations_mms": round(random.uniform(0.1, 2.5) * (active_power / MAX_POWER_KW), 2) if is_operational else 0
    }
    return data

def load_state():
    """Loads the last saved timestamp from the state file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            # Cargar como datetime con timezone UTC
            return datetime.fromisoformat(state['last_timestamp']).replace(tzinfo=timezone.utc)
    return START_DATE

def save_state(timestamp):
    """Saves the current timestamp to the state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_timestamp': timestamp.isoformat()}, f)

def main():
    """Main function to generate the dataset."""
    print(f"Dataset will be saved to: {os.path.abspath(OUTPUT_FILE)}")
    print(f"Generating data from {START_DATE} to {END_DATE}")
    print(f"Interval: {TIME_INTERVAL_MINUTES} minutes")
    print(f"Farms: {NUM_FARMS}, Turbines per farm: {TURBINES_PER_FARM}")
    
    start_time = time.time()
    current_date = load_state()

    if current_date > START_DATE:
        print(f"Resuming data generation from: {current_date}")
        output_mode = 'a'
    else:
        print("Starting new data generation.")
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        output_mode = 'w'

    total_intervals = int((END_DATE - START_DATE).total_seconds() / (TIME_INTERVAL_MINUTES * 60))
    total_records = total_intervals * NUM_FARMS * TURBINES_PER_FARM
    
    generated_count = 0
    if current_date > START_DATE:
        resumed_intervals = int((current_date - START_DATE).total_seconds() / (TIME_INTERVAL_MINUTES * 60))
        generated_count = resumed_intervals * NUM_FARMS * TURBINES_PER_FARM

    last_progress_percent = -1

    try:
        with open(OUTPUT_FILE, output_mode) as f:
            while current_date < END_DATE:
                for farm_id in range(1, NUM_FARMS + 1):
                    for turbine_num in range(1, TURBINES_PER_FARM + 1):
                        turbine_id = (farm_id - 1) * TURBINES_PER_FARM + turbine_num
                        record = generate_turbine_data(farm_id, turbine_id, current_date)
                        
                        # Escribir al archivo usando json_util para preservar datetime
                        f.write(json_util.dumps(record) + '\n')
                        generated_count += 1

                current_date += timedelta(minutes=TIME_INTERVAL_MINUTES)
                
                # Progress Update
                progress_percent = int((generated_count / total_records) * 100)
                if progress_percent > last_progress_percent:
                    last_progress_percent = progress_percent
                    elapsed_time = time.time() - start_time
                    records_per_sec = generated_count / elapsed_time if elapsed_time > 0 else 0
                    print(f"Progress: {progress_percent}% | Records: {generated_count}/{total_records} | Speed: {records_per_sec:.0f} rec/s")
                    save_state(current_date)

        print("\n✅ Dataset generation complete!")
        print(f"Total records: {generated_count}")
        print(f"Total time: {time.time() - start_time:.2f}s")
        
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)

    except KeyboardInterrupt:
        print("\n⚠️  Generation paused by user. Saving state...")
        save_state(current_date)
        print("State saved. Run the script again to resume.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Saving state before exiting...")
        save_state(current_date)
        print("State saved. Run the script again to resume.")

if __name__ == "__main__":
    main()