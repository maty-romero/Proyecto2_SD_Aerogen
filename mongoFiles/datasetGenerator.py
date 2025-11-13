
import json
import random
import time
from datetime import datetime, timedelta
import os

# --- Configuration ---
NUM_FARMS = 1
TURBINES_PER_FARM = 5
START_DATE = datetime(2025, 1, 1)
END_DATE = START_DATE + timedelta(days=365)
TIME_INTERVAL_MINUTES = 20
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

    is_operational = active_power > 0 and random.random() > 0.01 # 1% chance of fault
    operational_state = "operational" if is_operational else random.choice(["fault", "maintenance"])

    if not is_operational:
        wind_speed = 0
        active_power = 0

    rotor_speed = round((wind_speed / RATED_SPEED) * 20, 2) if is_operational else 0 # Max 20 RPM
    blade_pitch = round((wind_speed / RATED_SPEED) * 15, 2) if is_operational else 0 # Max 15 degrees

    data = {
        "farm_id": farm_id,
        "farm_name": f"Farm-{farm_id:003d}",
        "turbine_id": turbine_id,
        "turbine_name": f"T-{turbine_id:003d}",
        "timestamp": timestamp.isoformat() + "Z",
        "timestamp_str": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "capacity_mw": CAPACITY_MW,
        "operational_state": operational_state,
        "active_power_kw": active_power,
        "reactive_power_kvar": round(active_power * 0.4, 2), # Simplified relation
        "generated_current_a": round((active_power * 1000) / (400 * 1.732), 2) if is_operational else 0,
        "output_voltage_v": 400 + random.uniform(-5, 5) if is_operational else 0,
        "wind_speed_mps": wind_speed,
        "wind_direction_deg": random.randint(0, 359),
        "yaw_position_deg": random.randint(0, 359),
        "rotor_speed_rpm": rotor_speed,
        "blade_pitch_angle_deg": blade_pitch,
        "gear_temperature_c": round(40 + (active_power / MAX_POWER_KW) * 40 + random.uniform(-2, 2), 1),
        "bearing_temperature_c": round(35 + (active_power / MAX_POWER_KW) * 35 + random.uniform(-2, 2), 1),
        "vibrations_mms": round(random.uniform(0.1, 2.5) * (active_power / MAX_POWER_KW), 2)
    }
    return data

def load_state():
    """Loads the last saved timestamp from the state file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return datetime.fromisoformat(state['last_timestamp'])
    return START_DATE

def save_state(timestamp):
    """Saves the current timestamp to the state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_timestamp': timestamp.isoformat()}, f)

def main():
    """Main function to generate the dataset."""
    print(f"Dataset will be saved to: {os.path.abspath(OUTPUT_FILE)}")
    start_time = time.time()
    current_date = load_state()

    if current_date > START_DATE:
        print(f"Resuming data generation from: {current_date}")
        output_mode = 'a'
    else:
        print("Starting new data generation.")
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE) # Start fresh
        output_mode = 'w'

    total_intervals = (END_DATE - START_DATE) // timedelta(minutes=TIME_INTERVAL_MINUTES)
    total_records = total_intervals * NUM_FARMS * TURBINES_PER_FARM
    
    generated_count = 0
    if current_date > START_DATE:
        resumed_intervals = (current_date - START_DATE) // timedelta(minutes=TIME_INTERVAL_MINUTES)
        generated_count = resumed_intervals * NUM_FARMS * TURBINES_PER_FARM

    last_progress_percent = -1

    try:
        with open(OUTPUT_FILE, output_mode) as f:
            while current_date < END_DATE:
                for farm_id in range(1, NUM_FARMS + 1):
                    for turbine_num in range(1, TURBINES_PER_FARM + 1):
                        turbine_id = (farm_id - 1) * TURBINES_PER_FARM + turbine_num
                        record = generate_turbine_data(farm_id, turbine_id, current_date)
                        f.write(json.dumps(record) + '\n')
                        generated_count += 1

                current_date += timedelta(minutes=TIME_INTERVAL_MINUTES)
                
                # --- Progress Update ---
                progress_percent = int((generated_count / total_records) * 100)
                if progress_percent > last_progress_percent:
                    last_progress_percent = progress_percent
                    elapsed_time = time.time() - start_time
                    print(f"Progress: {progress_percent}% complete. Elapsed time: {elapsed_time:.2f}s")
                    save_state(current_date)

        print("\nDataset generation complete!")
        print(f"Total records: {generated_count}")
        print(f"Total time: {time.time() - start_time:.2f}s")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE) # Clean up state file on success

    except KeyboardInterrupt:
        print("\nGeneration paused by user. Saving state...")
        save_state(current_date)
        print("State saved. Run the script again to resume.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Saving state before exiting...")
        save_state(current_date)
        print("State saved. Run the script again to resume.")

if __name__ == "__main__":
    main()
