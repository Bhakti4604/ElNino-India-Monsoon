
from pathlib import Path

import numpy as np
import xarray as xr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "RF25_ind2020_rfp25.nc"

with xr.open_dataset(INPUT_FILE) as ds:
    rainfall = ds["RAINFALL"]

    missing_by_latitude = rainfall.isnull().all(
        dim=("TIME", "LONGITUDE")
    ).sum().item()

    missing_by_longitude = rainfall.isnull().all(
        dim=("TIME", "LATITUDE")
    ).sum().item()

    total_cells = rainfall.size
    missing_cells = rainfall.isnull().sum().item()
    valid_cells = total_cells - missing_cells

    print("MISSING-VALUE DIAGNOSTICS")
    print(f"Total observations: {total_cells:,}")
    print(f"Missing observations: {missing_cells:,}")
    print(f"Valid observations: {valid_cells:,}")
    print(f"Latitude rows entirely missing: {missing_by_latitude}")
    print(f"Longitude columns entirely missing: {missing_by_longitude}")

    print("\nRAINFALL VALUE RANGE")
    print(f"Minimum valid value: {float(rainfall.min(skipna=True).item())}")
    print(f"Maximum valid value: {float(rainfall.max(skipna=True).item())}")

    print("\nSAMPLE GRID POINTS")
    for latitude, longitude in [
        (18.5, 73.8),
        (19.0, 73.0),
        (28.6, 77.2),
        (15.0, 75.0),
    ]:
        point = rainfall.sel(
            LATITUDE=latitude,
            LONGITUDE=longitude,
            method="nearest",
        )
        print(
            f"Requested ({latitude}, {longitude}); "
            f"selected ({float(point.LATITUDE)}, "
            f"{float(point.LONGITUDE)}); "
            f"valid days: {int(point.notnull().sum().item())}/366"
        )
