# 404-Hackthon-Project
Here’s an illustration matching the **latest architecture** (backend serial read → Excel log → Flask web interface with searchable HTML table).

---

# Smart Sensor Diagnostics and Visualization Platform

### Overview

This project provides an **automated sensor diagnostics and visualization system** that integrates hardware (mega2560 + ToF sensors), a Python backend for serial data processing, and a Flask-based web interface for real-time inspection of sensor status.
It replaces the traditional manual workflow — where engineers test each board by hand and record data line-by-line — with a semi-automated, structured, and traceable process.

---

## 1. Problem Background

In many mechatronics and embedded labs, students or engineers spend hours checking whether sensors and circuit boards are functioning properly.
Common issues include:

* Faulty I²C connections or damaged boards not detected until deployment.
* Time-consuming manual testing via Arduino Serial Monitor.
* Missing historical records of which sensors failed and why.

**Goal:**
Create an end-to-end workflow that automatically logs sensor health data and displays it in an intuitive web interface — making hardware validation faster, clearer, and reproducible.

---

## 2. Solution Architecture

```
┌──────────┐   Serial Data (CSV)    ┌──────────────────────┐
│ mega  &  │  → via USB COM Port →  │ serial_to_excel.py   │
│  Sensors │                        │ (Python Script)      │
└──────────┘                        └──────────┬───────────┘
                                               │
                                               ▼
                                   ┌─────────────────────┐
                                   │ sensor_status.xlsx │
                                   │ + status snapshot  │
                                   │ + change history   │
                                   └──────────┬─────────┘
                                               │
                            ┌──────────────────▼──────────────────┐
                            │   Flask Backend (app.py)            │
                            │   - reads Excel via pandas          │
                            │   - provides / and /export routes   │
                            └──────────┬──────────────────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │ Frontend (index.html)       │
                        │ - Jinja template rendering  │
                        │ - Search bar + data table   │
                        └─────────────────────────────┘
```

* **Hardware Layer:** Mega2560 with VL53L0X / VL53L1X / VL6180X ToF sensors prints diagnostic info via serial.
* **Data Collection Layer:** `serial_to_excel.py` reads serial output, parses it into structured fields, and updates an Excel file.
* **Backend Layer:** Flask reads Excel files, filters results, and renders them to a searchable web page.
* **Frontend Layer:** `index.html` (Jinja2 template) provides a clean search interface and a live data table.

The following figure shows the whole system architecture with details.

<img width="1117" height="884" alt="image" src="https://github.com/user-attachments/assets/29edc99e-5a0c-4f10-82ff-238de1824da3" />

---

## 3. Problem-Solving Workflow

### (1) Problem Definition → Requirements

* Detect malfunctioning or interfered sensors automatically.
* Store both **latest status** and **change history**.
* Provide a lightweight visualization interface accessible to non-programmers.
* Support export for documentation or teaching purposes.

### (2) Requirement Breakdown → Data Flow

1. Serial data stream (from mega2560) is captured and parsed into structured rows.
2. Status updates are written only when changes occur (avoiding redundant logs).
3. Excel file serves as both data store and validation record.
4. Flask web app reads the Excel file dynamically, allowing users to search sensors by name or ID.

The following figure shows the time-sequence of data-flows.

<img width="1620" height="930" alt="image" src="https://github.com/user-attachments/assets/88962e71-a390-4736-8229-cf9fbb9b82b5" />



### (3) Technology Decisions

| Layer        | Tool                                  | Reason                                     |
| ------------ | ------------------------------------- | ------------------------------------------ |
| Hardware     | Mega2560 + VL53 series                   | Widely used, easy serial output            |
| Data Logging | Python + pySerial + pandas + openpyxl | Fast prototyping, Excel compatibility      |
| Backend      | Flask                                 | Lightweight, integrates easily with pandas |
| Frontend     | HTML + CSS + Jinja                    | Minimal setup, readable for beginners      |
| File Storage | Excel (.xlsx)                         | Easy verification by mentors and students  |

### (4) Implementation Highlights

* **Selective logging:** Data written only when sensor status changes.
* **Dual-sheet design:**

  * *Status Sheet* → current state of each sensor.
  * *Changes Sheet* → full history with timestamps.
* **Searchable web UI:** Flask injects data into `index.html` for keyword filtering.
* **Export function:** `/export` route can generate Markdown or summary reports.

---

## 4. Engineering Features

* **Maintainability:** Excel format for inspection + clear modular scripts (`serial_to_excel.py`, `app.py`).
* **Scalability:** Can later swap Excel for SQLite/MySQL and integrate MQTT or HTTP APIs.
* **Portability:** Runs on any PC with Python 3 and USB serial.
* **Transparency:** Every record is timestamped and human-readable.

---

## 5. How to Run

### 1. Hardware

Connect Mega2560 and sensors via I²C, upload the Arduino test sketch that prints:

```
ID,Sensor,Working,Status,Notes
1,VL53L0X,False,Error,I2C Failure
2,VL53L1X,True,Warning,Glass interference detected
3,VL6180X,True,OK,Stable
```

### 2. Backend

Run:

```bash
python serial_to_excel.py
```

This continuously reads serial data and updates `sensor_status.xlsx`.

Then start the Flask web server:

```bash
python app.py
```

### 3. Frontend

Open the local web page (usually [http://127.0.0.1:5000/](http://127.0.0.1:5000/)),
type a sensor name in the search bar (e.g., `VL53L1X`), and view the table of results.

---

## 6. Future Improvements

* Replace Excel with SQLite for multi-user concurrent access.
* Add live updates via Server-Sent Events (SSE) or WebSocket.
* Visualize sensor trends with charts.
* Extend to cloud integration for remote diagnostics.

---

## 7. Credits

Developed for **CISSA Catalyst 2025 Hackathon** at the University of Melbourne.
Team focus: bridging **Mechatronics hardware diagnostics** with **Full-Stack Web Development**.
Mentor support: Senior software engineer (20+ years experience).

---

