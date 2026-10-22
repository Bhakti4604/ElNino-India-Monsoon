
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

rain_file = PROCESSED_DIR / "india_monsoon_2015_2024.csv"
oni_file = PROCESSED_DIR / "oni_clean.csv"
output_file = PROCESSED_DIR / "india_enso_monsoon_2015_2024.csv"

rain = pd.read_csv(rain_file)
oni = pd.read_csv(oni_file)

# Standardise ONI columns and remove accidental whitespace.
oni.columns = oni.columns.str.strip()
oni["SEAS"] = oni["SEAS"].astype(str).str.strip()
oni["YR"] = pd.to_numeric(oni["YR"], errors="coerce")
oni["ANOM"] = pd.to_numeric(oni["ANOM"], errors="coerce")

# JJA and JAS represent overlapping 3-month ONI seasons
# within India's June–September monsoon period.
oni_monsoon = oni[
    oni["SEAS"].isin(["JJA", "JAS"])
    & oni["YR"].between(2015, 2024)
].copy()

oni_summary = (
    oni_monsoon.groupby("YR", as_index=False)
    .agg(
        Monsoon_ONI_Mean=("ANOM", "mean"),
        ONI_Seasons_Available=("ANOM", "count"),
    )
    .rename(columns={"YR": "Year"})
)

comparison = rain.merge(oni_summary, on="Year", how="left")

# Descriptive anomaly categories only; these are not official
# NOAA ENSO episode classifications.
comparison["ENSO_Anomaly_Group"] = comparison["Monsoon_ONI_Mean"].apply(
    lambda x: (
        "Warm anomaly" if pd.notna(x) and x >= 0.5
        else "Cool anomaly" if pd.notna(x) and x <= -0.5
        else "Near-neutral anomaly" if pd.notna(x)
        else "Missing ONI"
    )
)

comparison.to_csv(output_file, index=False)

print("\nCOMPARISON FILE CREATED")
print(comparison.to_string(index=False))
print("\nMissing ONI averages:", comparison["Monsoon_ONI_Mean"].isna().sum())

if comparison["Monsoon_ONI_Mean"].notna().sum() >= 3:
    correlation = comparison[
        ["Monsoon_Mean_Grid_Seasonal_Rainfall_mm", "Monsoon_ONI_Mean"]
    ].corr().iloc[0, 1]

    print(f"Pearson correlation (10-year comparison): {correlation:.3f}")

print("\nSaved:", output_file)
