"""
Campus Energy-Use Analyser
A beginner-friendly Python capstone project.

Course concepts demonstrated:
1. Functions and control flow
2. Lists, dictionaries, CSV and JSON file handling
3. Classes and object-oriented programming
4. NumPy numerical operations
5. Pandas data analysis
6. Matplotlib visualisations
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = Path(__file__).with_name("energy_readings.csv")
OUTPUT_DIR = Path(__file__).with_name("output")
OUTPUT_DIR.mkdir(exist_ok=True)


class Building:
    """Represents one campus building and its electricity readings."""

    def __init__(self, name, readings):
        self.name = name
        self.readings = readings

    def total_consumption(self):
        return float(self.readings["daily_consumption_kwh"].sum())

    def average_consumption(self):
        return float(self.readings["daily_consumption_kwh"].mean())

    def highest_consumption(self):
        row = self.readings.loc[self.readings["daily_consumption_kwh"].idxmax()]
        return row["date"].strftime("%Y-%m-%d"), float(row["daily_consumption_kwh"])


def load_data(file_path=DATA_FILE):
    """Load meter readings, validate them and calculate daily consumption."""
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path.name}.")

    df = pd.read_csv(file_path)

    required = {"date", "building", "meter_reading_kwh"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["meter_reading_kwh"] = pd.to_numeric(
        df["meter_reading_kwh"], errors="coerce"
    )

    if df["date"].isna().any() or df["meter_reading_kwh"].isna().any():
        raise ValueError("The CSV contains an invalid date or meter reading.")

    if (df["meter_reading_kwh"] < 0).any():
        raise ValueError("Meter readings cannot be negative.")

    df = df.sort_values(["building", "date"]).reset_index(drop=True)

    # A meter reading is cumulative. Difference between consecutive readings
    # gives the electricity consumed during that day.
    df["daily_consumption_kwh"] = (
        df.groupby("building")["meter_reading_kwh"].diff()
    )

    # The first reading for each building is a starting meter value, not a
    # complete day's usage. It is therefore excluded from daily analysis.
    df = df.dropna(subset=["daily_consumption_kwh"]).copy()

    if (df["daily_consumption_kwh"] < 0).any():
        raise ValueError(
            "A meter reading decreased. Check for a meter reset or incorrect data."
        )

    return df


def make_buildings(df):
    """Create Building objects and store them in a dictionary."""
    building_objects = {}
    for name, group in df.groupby("building"):
        building_objects[name] = Building(name, group.copy())
    return building_objects


def show_overall_summary(df):
    """Display key campus-wide statistics using Pandas and NumPy."""
    values = df["daily_consumption_kwh"].to_numpy()

    print("\n========== CAMPUS ENERGY SUMMARY ==========")
    print(f"Buildings monitored : {df['building'].nunique()}")
    print(f"Days analysed       : {df['date'].nunique()}")
    print(f"Total consumption   : {np.sum(values):,.2f} kWh")
    print(f"Average daily use   : {np.mean(values):,.2f} kWh")
    print(f"Median daily use    : {np.median(values):,.2f} kWh")
    print(f"Highest daily use   : {np.max(values):,.2f} kWh")
    print("===========================================\n")


def show_building_comparison(buildings):
    """Print total and average consumption for every building."""
    rows = []
    for name, building in buildings.items():
        rows.append({
            "Building": name,
            "Total (kWh)": round(building.total_consumption(), 2),
            "Daily Average (kWh)": round(building.average_consumption(), 2)
        })

    summary = pd.DataFrame(rows).sort_values(
        "Total (kWh)", ascending=False
    )
    print("\n========== BUILDING-WISE COMPARISON ==========")
    print(summary.to_string(index=False))
    print("==============================================\n")


def detect_anomalies(df):
    """
    Detect unusually high daily consumption within each building.

    The rule used is:
    value > Q3 + 1.5 * IQR
    where IQR = Q3 - Q1.
    """
    flagged_groups = []

    for name, group in df.groupby("building"):
        q1 = group["daily_consumption_kwh"].quantile(0.25)
        q3 = group["daily_consumption_kwh"].quantile(0.75)
        iqr = q3 - q1
        upper_limit = q3 + 1.5 * iqr

        unusual = group[group["daily_consumption_kwh"] > upper_limit].copy()
        if not unusual.empty:
            unusual["upper_limit_kwh"] = upper_limit
            flagged_groups.append(unusual)

    print("\n========== UNUSUAL CONSUMPTION ALERTS ==========")
    if not flagged_groups:
        print("No unusually high readings were detected.")
        return pd.DataFrame()

    alerts = pd.concat(flagged_groups).sort_values(
        "daily_consumption_kwh", ascending=False
    )
    for _, row in alerts.iterrows():
        print(
            f"{row['building']} | {row['date'].strftime('%Y-%m-%d')} | "
            f"{row['daily_consumption_kwh']:.2f} kWh "
            f"(upper limit: {row['upper_limit_kwh']:.2f} kWh)"
        )
    print("Note: An alert indicates a reading worth checking; it does not prove a fault.")
    print("================================================\n")
    return alerts


def plot_building_totals(buildings):
    """Create a bar chart comparing total consumption."""
    names = list(buildings.keys())
    totals = [buildings[name].total_consumption() for name in names]

    plt.figure(figsize=(10, 5))
    plt.bar(names, totals)
    plt.title("Total Electricity Consumption by Building")
    plt.xlabel("Campus Building")
    plt.ylabel("Consumption (kWh)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    path = OUTPUT_DIR / "building_comparison.png"
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved to: {path}")


def plot_daily_trend(df):
    """Create a line graph of daily consumption for each building."""
    pivot = df.pivot_table(
        index="date",
        columns="building",
        values="daily_consumption_kwh",
        aggfunc="sum"
    )

    plt.figure(figsize=(11, 6))
    for building_name in pivot.columns:
        plt.plot(pivot.index, pivot[building_name], marker="o",
                 markersize=3, label=building_name)

    plt.title("Daily Electricity Consumption Trend")
    plt.xlabel("Date")
    plt.ylabel("Daily Consumption (kWh)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = OUTPUT_DIR / "daily_consumption_trend.png"
    plt.savefig(path, dpi=150)
    plt.show()
    print(f"Chart saved to: {path}")


def export_reports(df, buildings, alerts):
    """Export summary information to CSV and JSON files."""
    summary_rows = []
    for name, building in buildings.items():
        summary_rows.append({
            "building": name,
            "total_consumption_kwh": round(building.total_consumption(), 2),
            "average_daily_consumption_kwh": round(
                building.average_consumption(), 2
            )
        })

    summary_df = pd.DataFrame(summary_rows).sort_values(
        "total_consumption_kwh", ascending=False
    )
    summary_df.to_csv(OUTPUT_DIR / "building_summary.csv", index=False)

    report = {
        "report_title": "Campus Energy-Use Report",
        "records_analysed": int(len(df)),
        "buildings_analysed": int(df["building"].nunique()),
        "total_consumption_kwh": round(
            float(df["daily_consumption_kwh"].sum()), 2
        ),
        "average_daily_consumption_kwh": round(
            float(df["daily_consumption_kwh"].mean()), 2
        ),
        "building_summary": summary_rows,
        "unusual_readings": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "building": row["building"],
                "consumption_kwh": round(
                    float(row["daily_consumption_kwh"]), 2
                )
            }
            for _, row in alerts.iterrows()
        ] if not alerts.empty else []
    }

    with open(OUTPUT_DIR / "energy_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"\nReports exported to: {OUTPUT_DIR}")
    print("- building_summary.csv")
    print("- energy_report.json")


def main():
    """Main menu and program control."""
    try:
        df = load_data()
        buildings = make_buildings(df)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"Error: {error}")
        return

    print("\n*** CAMPUS ENERGY-USE ANALYSER ***")
    print(f"Loaded {len(df)} daily consumption records.")

    while True:
        print("\nChoose an option:")
        print("1. Overall campus summary")
        print("2. Building-wise comparison")
        print("3. Detect unusual consumption")
        print("4. Plot building-wise consumption")
        print("5. Plot daily consumption trends")
        print("6. Export CSV and JSON reports")
        print("7. Run all analyses")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_overall_summary(df)
        elif choice == "2":
            show_building_comparison(buildings)
        elif choice == "3":
            detect_anomalies(df)
        elif choice == "4":
            plot_building_totals(buildings)
        elif choice == "5":
            plot_daily_trend(df)
        elif choice == "6":
            alerts = detect_anomalies(df)
            export_reports(df, buildings, alerts)
        elif choice == "7":
            show_overall_summary(df)
            show_building_comparison(buildings)
            alerts = detect_anomalies(df)
            plot_building_totals(buildings)
            plot_daily_trend(df)
            export_reports(df, buildings, alerts)
        elif choice == "0":
            print("Thank you for using the Campus Energy-Use Analyser!")
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 7.")


if __name__ == "__main__":
    main()
