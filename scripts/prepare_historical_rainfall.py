
from pathlib import Path
import re

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

BOUNDARY_FILE = RAW_DIR / "india_boundary.geojson"
DAILY_OUTPUT = PROCESSED_DIR / "india_daily_rainfall_2015_2024.csv"
MONSOON_OUTPUT = PROCESSED_DIR / "india_monsoon_2015_2024.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load India's boundary
boundary = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")
india_geometry = boundary.geometry.union_all()

files = sorted(RAW_DIR.glob("RF25_ind????_rfp25.nc"))

if not files:
    raise FileNotFoundError(f"No rainfall NetCDF files found in {RAW_DIR}")

daily_results = []
monsoon_results = []
reference_lat = None
reference_lon = None
inside_india = None

for file in files:
    match = re.search(r"RF25_ind(\d{4})_rfp25\.nc$", file.name)
    if not match:
        continue

    year = int(match.group(1))
    print(f"Processing {year}...")

    with xr.open_dataset(file) as ds:
        rainfall = ds["RAINFALL"]

        lat = ds["LATITUDE"].values
        lon = ds["LONGITUDE"].values

        # Build the India grid mask once and reuse it.
        if inside_india is None:
            lon_grid, lat_grid = np.meshgrid(lon, lat)
            points = gpd.GeoSeries(
                gpd.points_from_xy(lon_grid.ravel(), lat_grid.ravel()),
                crs="EPSG:4326",
            )
            inside_india = points.intersects(india_geometry).to_numpy()
            inside_india = inside_india.reshape(len(lat), len(lon))
            reference_lat = lat.copy()
            reference_lon = lon.copy()

            print(
                "Grid points intersecting boundary:",
                int(inside_india.sum()),
            )
        else:
            if not (
                np.array_equal(lat, reference_lat)
                and np.array_equal(lon, reference_lon)
            ):
                raise ValueError(
                    f"Grid coordinates differ from the first file: {file.name}"
                )

        # Retain grid-cell centres intersecting the selected India boundary.
        india_rain = rainfall.where(inside_india)

        spatial_dims = ("LATITUDE", "LONGITUDE")

        daily_mean = india_rain.mean(
            dim=spatial_dims, skipna=True
        ).to_series()
        daily_max = india_rain.max(
            dim=spatial_dims, skipna=True
        ).to_series()
        daily_min = india_rain.min(
            dim=spatial_dims, skipna=True
        ).to_series()
        grid_count = india_rain.notnull().sum(
            dim=spatial_dims
        ).to_series()

        daily = pd.DataFrame({
            "Date": pd.to_datetime(daily_mean.index),
            "Mean_Rainfall_mm": daily_mean.to_numpy(),
            "Max_Grid_Rainfall_mm": daily_max.to_numpy(),
            "Min_Grid_Rainfall_mm": daily_min.to_numpy(),
            "Grid_Points_Reported": grid_count.to_numpy(),
        })

        daily_results.append(daily)

        # June through September monsoon season
        daily["Year"] = daily["Date"].dt.year
        monsoon = daily[
            (daily["Date"].dt.month >= 6)
            & (daily["Date"].dt.month <= 9)
        ]

        if monsoon.empty:
            print(f"Warning: no June–September observations for {year}")
            continue

        monsoon_results.append({
            "Year": year,
            "Monsoon_Days": len(monsoon),
            "Monsoon_Mean_Daily_Grid_Rainfall_mm":
                monsoon["Mean_Rainfall_mm"].mean(),
            "Monsoon_Mean_Grid_Seasonal_Rainfall_mm":
                monsoon["Mean_Rainfall_mm"].sum(),
            "Monsoon_Max_Daily_Grid_Rainfall_mm":
                monsoon["Max_Grid_Rainfall_mm"].max(),
            "Average_Grid_Points_Reported":
                monsoon["Grid_Points_Reported"].mean(),
        })

# Combine all years
if not daily_results:
    raise ValueError("No valid rainfall data was processed.")

daily_all = pd.concat(daily_results, ignore_index=True)
daily_all = daily_all.sort_values("Date").drop_duplicates("Date")
daily_all.to_csv(DAILY_OUTPUT, index=False, date_format="%Y-%m-%d")

monsoon_all = pd.DataFrame(monsoon_results).sort_values("Year")
monsoon_all.to_csv(MONSOON_OUTPUT, index=False)

# Validation summary
print("\nPROCESSING COMPLETE")
print("Years processed:", sorted(daily_all["Date"].dt.year.unique().tolist()))
print("Daily rows:", len(daily_all))
print("Date range:", daily_all["Date"].min().date(),
      "to", daily_all["Date"].max().date())
print("Missing daily means:", daily_all["Mean_Rainfall_mm"].isna().sum())
print("Daily grid-point counts:",
      int(daily_all["Grid_Points_Reported"].min()), "to",
      int(daily_all["Grid_Points_Reported"].max()))
print("\nMonsoon summary:")
print(monsoon_all.to_string(index=False))
print("\nSaved files:")
print(DAILY_OUTPUT)
print(MONSOON_OUTPUT)
