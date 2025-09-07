import random
from datetime import datetime, timedelta
import openpyxl

# Predefined pool of sensors
SENSORS = [
    {"sensor": "VL53L1X", "perfomace_summary": "Functional, longer range, but glass interference noted"},
    {"sensor": "VL6180X", "perfomace_summary": "Stable, but still affected by transparent surfaces"},
    {"sensor": "SEN0381", "perfomace_summary": "High accuracy, needs calibration in special environments"},
    {"sensor": "SEN0531", "perfomace_summary": "Reliable, slightly unstable near reflective surfaces"},
]

STATUSES = ["Working", "Affected", "Error", "Offline"]

def generate_sensor_data(max_rows: int = 5):
    rows = []
    num_rows = random.randint(1, max_rows)  # Random number of rows
    base_time = datetime.now()

    for i in range(num_rows):
        sensor = random.choice(SENSORS)
        row = {
            "sensor": sensor["sensor"],
            "i2c_functionality": random.choice(STATUSES),
            "perfomace_summary": sensor["perfomace_summary"],
            "timestamp": (base_time + timedelta(seconds=i*5)).isoformat(timespec="seconds"),

        }
        rows.append(row)

    return rows

if __name__ == "__main__":
    data = generate_sensor_data(random.randint(1, 10))
    print("sensor\ti2c_functionality\perfomace_summary\ttimestamp")
    for row in data:
        print(
            f"{row['sensor']}\t"
            f"{row['i2c_functionality']}\t"
            f"{row['perfomace_summary']}\t"
            f"{row['timestamp']}"
        )
        
        excel_path = "sensor test 1.0 .xlsx"
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        for row in data:
            ws.append([
                row["sensor"],
                row["i2c_functionality"],
                row["perfomace_summary"],
                row["timestamp"],
            ])

        wb.save(excel_path)
