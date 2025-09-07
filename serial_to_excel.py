# import csv
# import time
# from datetime import datetime
# from pathlib import Path

# import pandas as pd
# import serial


# PORT = "COM4"      # my serial
# BAUD = 115200
# OUT  = Path("sensor_status.xlsx")
# COLUMNS = ["id", "sensor", "working", "affected", "note"]

# def parse_csv_line(line: str):
#     """Parse a line of CSV using csv.reader, supporting commas within quotes."""
#     rows = list(csv.reader([line]))
#     if not rows or len(rows[0]) < 5:
#         return None
#     r = rows[0]
#     # If there is a comma in the remarks, csv.reader has already split it.
#     return {
#         "id": r[0].strip(),
#         "sensor": r[1].strip(),
#         "working": r[2].strip(),
#         "affected": r[3].strip(),
#         "note": ",".join(r[4:]).strip() if len(r) > 5 else r[4].strip(),
#     }

# def records_equal(a: dict, b: dict) -> bool:
#     """Compare whether the four key fields are completely identical (case-insensitive comparison can be enabled as needed)"""
#     if a is None or b is None:
#         return False
#     return (
#         a.get("sensor")   == b.get("sensor") and
#         a.get("working")  == b.get("working") and
#         a.get("affected") == b.get("affected") and
#         a.get("note")     == b.get("note")
#     )

# def write_excel_if_changed(status_map: dict, changes_log: list):
#     """Write the latest status and change history into Excel (call this function only when there are any changes)）"""
#     # Status table: Current latest status snapshot
#     status_df = pd.DataFrame(list(status_map.values()), columns=COLUMNS)
#     # Make the digital sorting of IDs more user-friendly
#     try:
#         status_df["id_num"] = status_df["id"].astype(int)
#         status_df = status_df.sort_values("id_num").drop(columns=["id_num"])
#     except Exception:
#         status_df = status_df.sort_values("id")

#     # Changes Table: History of Changes (with timestamps)
#     changes_df = pd.DataFrame(changes_log, columns=["timestamp", *COLUMNS])

#     with pd.ExcelWriter(OUT, engine="openpyxl", mode="w") as w:
#         status_df.to_excel(w, index=False, sheet_name="Status")
#         changes_df.to_excel(w, index=False, sheet_name="Changes")

# def main():
#     print(f"Opening {PORT} @ {BAUD} …  (If the port is in use, please first close the Arduino serial monitor.)")
#     last_seen_by_id = {}   # id -> The most recent record received (used for comparing whether there has been any change)
#     status_by_id    = {}   # id -> Latest status (for the Status table)
#     changes_log     = []   # Change history (a new entry is added only when there is a change)

#     with serial.Serial(PORT, BAUD, timeout=1) as ser:
#         header_seen = False
#         while True:
#             raw = ser.readline().decode("utf-8", errors="ignore").strip()
#             if not raw:
#                 continue

#             # Skip the header row
#             if not header_seen and raw.lower().startswith("id,"):
#                 header_seen = True
#                 print("Header received.")
#                 continue

#             rec = parse_csv_line(raw)
#             if not rec:
#                 continue

#             rid = rec["id"]
#             prev = last_seen_by_id.get(rid)

#             # Only record/commit the changes when the state actually changes.
#             if not records_equal(prev, rec):
#                 # Update "most recent" and "latest status"
#                 last_seen_by_id[rid] = rec
#                 status_by_id[rid] = rec

#                 # Record a change history (with timestamp)
#                 changes_log.append([
#                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     rec["id"], rec["sensor"], rec["working"], rec["affected"], rec["note"]
#                 ])

#                 # Write in Excel (write only when there are changes)
#                 write_excel_if_changed(status_by_id, changes_log)

#                 print(f'CHANGED: id={rec["id"]} sensor={rec["sensor"]} '
#                       f'{rec["working"]}/{rec["affected"]}')

#             # If they are exactly the same, then quietly skip it and do not print or create any files.

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\nStopped by user. Final saved:", OUT.resolve())



import os
import re
import time
import serial
import pandas as pd
from datetime import datetime

# ==== config ====
SERIAL_PORT = "COM4"      # my serial
BAUD_RATE   = 115200
RUN_SECONDS = 9000          # duration to run (seconds)
OUTPUT_DIR  = "./logs"    # output directory
# avoid overwriting previous logs
RUN_TAG = datetime.now().strftime("%Y%m%d-%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"sensor_status.xlsx")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== regularization ====
# 同行双传感器距离（推荐）：[L0X 0x2A] Distance (mm): 42   [L1X 0x29] Distance (mm): 33
DUO_DIST_RE = re.compile(
    r"\[L0X\s+0x(?P<addr0>[0-9A-Fa-f]+)\]\s*Distance\s*\(mm\):\s*(?P<d0>\d+)\s+"
    r"\[L1X\s+0x(?P<addr1>[0-9A-Fa-f]+)\]\s*Distance\s*\(mm\):\s*(?P<d1>\d+)"
)

# 单行单传感器距离（容错）：[L0X 0x2A] Distance (mm): 42
SINGLE_DIST_RE = re.compile(
    r"\[(?P<tag>L0X|L1X)\s+0x(?P<addr>[0-9A-Fa-f]+)\]\s*Distance\s*\(mm\):\s*(?P<d>\d+)"
)

# 状态行：VL53L0X  ✅ Working / VL53L1X  ❌ I2C failure
STATUS_RE = re.compile(
    r"^(?P<name>VL53L0X|VL53L1X)\s+[✅❌]\s+(?P<status>.+)$"
)

# 传感器名映射（把 L0X/L1X 标签统一成人类可读名）
TAG2NAME = {
    "L0X": "VL53L0X",
    "L1X": "VL53L1X",
}

# 运行时缓存：记录最新状态（Working / I2C failure）
latest_status = {"VL53L0X": None, "VL53L1X": None}

# 累积的行
rows = []

def push_row(sensor, address_hex, distance_mm=None, status=None):
    now = datetime.now()
    row = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "sensor": sensor,                       # VL53L0X / VL53L1X
        "address": f"0x{address_hex.upper()}" if address_hex else "",
        "distance_mm": int(distance_mm) if distance_mm is not None else None,
        "status": status if status is not None else latest_status.get(sensor),
    }
    rows.append(row)
    return rows

def parse_line(line: str):
    line = line.strip()
    if not line:
        return

    # 1) 先尝试“双传感器同一行距离”
    m = DUO_DIST_RE.search(line)
    if m:
        addr0, d0 = m.group("addr0"), m.group("d0")
        addr1, d1 = m.group("addr1"), m.group("d1")
        push_row("VL53L0X", addr0, distance_mm=d0)
        push_row("VL53L1X", addr1, distance_mm=d1)
        return

    # 2) 单传感器距离
    m = SINGLE_DIST_RE.search(line)
    if m:
        tag, addr, d = m.group("tag"), m.group("addr"), m.group("d")
        sensor = TAG2NAME.get(tag, tag)
        push_row(sensor, addr, distance_mm=d)
        return

    # 3) 状态行
    m = STATUS_RE.search(line)
    if m:
        name, status = m.group("name"), m.group("status").strip()
        latest_status[name] = status
        # 也落一行，方便时间轴回放
        push_row(name, address_hex=None, distance_mm=None, status=status)
        return

    # 其他杂项行不处理，但你也可以打印看看
    # print("UNPARSED:", line)

def read_and_log():
    start = time.time()
    print(f"Opening {SERIAL_PORT} @ {BAUD_RATE} …")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # 等 Arduino 重启
            print("Connected. Reading… (Ctrl+C to stop)")
            while time.time() - start < RUN_SECONDS:
                if ser.in_waiting:
                    line = ser.readline().decode("utf-8", errors="ignore")
                    print("Received:", line.strip())
                    row = parse_line(line)
                    save_xlsx()
                    rows=[]
            print(f"{RUN_SECONDS} seconds elapsed. Stopping.")
    except KeyboardInterrupt:
        print("Stopped by user.")
    except serial.SerialException as e:
        print("Serial error:", e)

def save_xlsx():
    if not rows:
        print("No data to save.")
        return
    df = pd.DataFrame(rows, columns=["timestamp", "sensor", "address", "distance_mm", "status"])
    # 可选：只在状态变化或距离变化时保留（去重）
    df = df.drop_duplicates()
    # 保存
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="readings")
    print(f"Saved {len(df)} rows → {OUTPUT_FILE}")

if __name__ == "__main__":
    read_and_log()
