
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "oni_data.txt"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "oni_clean.csv"

def main():
    # Check that the source file exists
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {RAW_FILE}")

    # Read NOAA's whitespace-separated ASCII file
    df = pd.read_csv(
        RAW_FILE,
        sep=r"\s+",
        dtype={"SEAS": "string", "YR": "int64"},
        na_values=["-99.99", "-999.9", "-999.99"]
    )

    # Standardise column names
    df.columns = [column.strip().upper() for column in df.columns]

    required_columns = {"SEAS", "YR", "TOTAL", "ANOM"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")

    # Convert measurements to numeric values
    for column in ["TOTAL", "ANOM"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove invalid rows and check the season names
    valid_seasons = {
        "DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
        "JJA", "JAS", "ASO", "SON", "OND", "NDJ"
    }

    df = df.dropna(subset=["SEAS", "YR", "TOTAL", "ANOM"])
    df = df[df["SEAS"].isin(valid_seasons)].copy()

    # Categorise the temperature anomaly.
    # These are anomaly categories, not official ENSO episode labels.
    df["Anomaly_Category"] = "Neutral range"
    df.loc[df["ANOM"] >= 0.5, "Anomaly_Category"] = "Warm anomaly"
    df.loc[df["ANOM"] <= -0.5, "Anomaly_Category"] = "Cool anomaly"

    # Validate data
    if df.empty:
        raise ValueError("No valid observations remain after cleaning.")

    if df.duplicated(subset=["SEAS", "YR"]).any():
        raise ValueError("Duplicate season-year combinations detected.")

    # Export cleaned data
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, float_format="%.2f")

    print("ONI data preparation completed.")
    print(f"Rows: {len(df):,}")
    print(f"Date coverage by year: {df['YR'].min()}–{df['YR'].max()}")
    print(f"Missing values:\n{df.isna().sum()}")
    print(f"Anomaly categories:\n{df['Anomaly_Category'].value_counts()}")
    print(f"Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
