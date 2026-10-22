
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILE = PROJECT_ROOT / "data" / "processed" / "india_rainfall_2020.csv"

df = pd.read_csv(FILE, parse_dates=["Date"])

print("FINAL DATA QUALITY CHECK")
print(f"Rows: {len(df):,}")
print(f"Columns: {df.columns.tolist()}")
print(f"Missing values by column:\n{df.isna().sum()}")
print(f"Duplicate date-location rows: {df.duplicated(['Date', 'Latitude', 'Longitude']).sum():,}")

daily_counts = df.groupby("Date").size()
print(f"\nDates covered: {daily_counts.size}")
print(f"Minimum observations per date: {daily_counts.min():,}")
print(f"Maximum observations per date: {daily_counts.max():,}")
print(f"Dates with fewer than 4,620 observations: {(daily_counts < 4620).sum()}")

grid_counts = df.groupby(["Latitude", "Longitude"]).size()
print(f"\nUnique grid points: {len(grid_counts):,}")
print(f"Minimum observations per grid point: {grid_counts.min()}")
print(f"Maximum observations per grid point: {grid_counts.max()}")

print(f"\nRainfall minimum: {df['Rainfall_mm'].min():.2f} mm")
print(f"Rainfall maximum: {df['Rainfall_mm'].max():.2f} mm")
print(f"Negative rainfall values: {(df['Rainfall_mm'] < 0).sum():,}")

print("\nDaily observation counts:")
print(daily_counts.describe().to_string())
