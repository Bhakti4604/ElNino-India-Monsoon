
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "india_rainfall_2020.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "india_daily_rainfall_2020.csv"


def main():
    df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

    daily = (
        df.groupby("Date", as_index=False)
        .agg(
            Mean_Rainfall_mm=("Rainfall_mm", "mean"),
            Max_Grid_Rainfall_mm=("Rainfall_mm", "max"),
            Min_Grid_Rainfall_mm=("Rainfall_mm", "min"),
            Grid_Points_Reported=("Rainfall_mm", "count"),
        )
    )

    daily.to_csv(OUTPUT_FILE, index=False)

    print("DAILY SUMMARY CREATED")
    print(f"Rows: {len(daily):,}")
    print(f"Columns: {daily.columns.tolist()}")
    print(f"Output: {OUTPUT_FILE}")
    print("\nFirst five rows:")
    print(daily.head().to_string(index=False))
    print("\nSummary statistics:")
    print(daily[["Mean_Rainfall_mm", "Max_Grid_Rainfall_mm"]].describe().round(2))


if __name__ == "__main__":
    main()
