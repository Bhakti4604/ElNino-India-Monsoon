
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "rainfall_2020.csv"
BOUNDARY_FILE = PROJECT_ROOT / "data" / "raw" / "india_boundary.geojson"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "india_rainfall_2020.csv"


def main():
    for file_path in [INPUT_FILE, BOUNDARY_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

    print("Loading India boundary...")
    boundary = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")
    india_geometry = boundary.geometry.union_all()

    print("Loading rainfall CSV...")
    df = pd.read_csv(INPUT_FILE)

    original_rows = len(df)
    missing_before = int(df["Rainfall_mm"].isna().sum())

    print("Selecting grid points inside the boundary...")
    points = gpd.GeoDataFrame(
        df[["Latitude", "Longitude"]],
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",
    )

    inside = points.geometry.intersects(india_geometry)
    india_df = df.loc[inside].copy()

    boundary_rows = len(india_df)
    missing_inside = int(india_df["Rainfall_mm"].isna().sum())

    # Remove missing rainfall observations, but retain genuine zeros.
    india_df = india_df.dropna(subset=["Rainfall_mm"]).copy()
    india_df["Rainfall_mm"] = india_df["Rainfall_mm"].astype("float32")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    india_df.to_csv(OUTPUT_FILE, index=False)

    print("\nPREPARATION SUMMARY")
    print(f"Original grid rows: {original_rows:,}")
    print(f"Missing rainfall in original grid: {missing_before:,}")
    print(f"Rows inside selected boundary, before missing-value removal: {boundary_rows:,}")
    print(f"Missing rainfall inside boundary: {missing_inside:,}")
    print(f"Final valid rainfall observations: {len(india_df):,}")
    print(f"Valid zero-rainfall observations: {(india_df['Rainfall_mm'] == 0).sum():,}")
    print(f"Unique dates: {india_df['Date'].nunique():,}")
    print(f"Unique grid points: {india_df[['Latitude', 'Longitude']].drop_duplicates().shape[0]:,}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Output size: {OUTPUT_FILE.stat().st_size / (1024**2):.2f} MB")

    if not india_df.empty:
        print("\nFirst five rows:")
        print(india_df.head().to_string(index=False))


if __name__ == "__main__":
    main()
