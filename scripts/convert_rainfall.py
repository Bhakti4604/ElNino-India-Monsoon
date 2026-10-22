
from pathlib import Path

import pandas as pd
import xarray as xr

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "RF25_ind2020_rfp25.nc"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "rainfall_2020.csv"
)


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("Reading rainfall dataset...")

    with xr.open_dataset(INPUT_FILE) as ds:
        rainfall = ds["RAINFALL"]

        print(f"Dataset dimensions: {dict(ds.sizes)}")
        print(f"Rainfall units: {rainfall.attrs.get('units', 'unknown')}")

        print("Converting grid cells into rows...")

        df = rainfall.to_dataframe(name="Rainfall_mm").reset_index()

    df = df.rename(
        columns={
            "TIME": "Date",
            "LATITUDE": "Latitude",
            "LONGITUDE": "Longitude",
        }
    )

    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Preserve missing grid observations for now.
    # We will inspect missing values before deciding whether to filter them.
    df = df[["Date", "Latitude", "Longitude", "Rainfall_mm"]]

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nCONVERSION COMPLETE")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing rainfall values: {df['Rainfall_mm'].isna().sum():,}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / (1024**2):.2f} MB")
    print("\nFirst five rows:")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
