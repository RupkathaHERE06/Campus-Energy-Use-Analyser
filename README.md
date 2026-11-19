# Campus Energy-Use Analyser

## Project overview
This Python capstone analyses electricity-meter readings from five simulated campus buildings. It calculates daily consumption, compares buildings, flags unusually high readings, creates charts, and exports CSV/JSON reports.

**Important:** `energy_readings.csv` contains simulated sample data for demonstration. Replace it with authorised campus meter readings before presenting any result as real campus data.

## Files
- `campus_energy_analyser.py` — main Python application
- `energy_readings.csv` — sample cumulative meter readings
- `requirements.txt` — required Python libraries
- `output/` — charts and reports are created here when the program runs

## Requirements
Python 3.9 or later is recommended.

Install libraries:
```bash
python -m pip install -r requirements.txt
```

Run:
```bash
python campus_energy_analyser.py
```

## CSV format
The input CSV must contain these columns:
- `date` — date of the meter reading (`YYYY-MM-DD`)
- `building` — building name
- `meter_reading_kwh` — cumulative meter reading in kWh

Each building should have readings in date order. Daily consumption is calculated by subtracting the previous cumulative reading from the current reading. The first reading for each building is used as the starting point and is not counted as a full day's consumption.

## Anomaly detection
The program flags high daily values above `Q3 + 1.5 × IQR`, calculated separately for each building. This is a simple statistical screening rule, not proof of an equipment fault.

## Course concepts demonstrated
1. **Functions/control flow:** modular functions, loops, conditionals, menu.
2. **Data structures/file handling:** dictionaries, lists, CSV input, JSON output.
3. **OOP:** `Building` class with methods for consumption statistics.
4. **NumPy:** sum, mean, median and maximum calculations.
5. **Pandas:** data cleaning, grouping, differences, summaries and pivot tables.
6. **Visualisation/reporting:** Matplotlib bar and line charts, CSV/JSON exports.

## Suggested presentation sequence
1. Explain the problem: campus electricity use needs to be monitored.
2. Show the CSV and explain cumulative meter readings.
3. Demonstrate how the program calculates daily consumption.
4. Show the building comparison and anomaly alert.
5. Display the two charts.
6. Open the exported JSON report.

## Limitations and future improvements
- Sample data is simulated, not collected from actual campus meters.
- The anomaly rule can flag unusual usage but cannot identify its cause.
- A future version could use live smart-meter data, electricity tariffs, carbon-emission factors, and a graphical user interface.
