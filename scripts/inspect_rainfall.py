
from pathlib import Path
import xarray as xr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAINFALL_FILE = PROJECT_ROOT / "data" / "raw" / "RF25_ind2020_rfp25.nc"

if not RAINFALL_FILE.exists():
    raise FileNotFoundError(f"File not found: {RAINFALL_FILE}")

with xr.open_dataset(RAINFALL_FILE) as ds:
    print("DATASET SUMMARY")
    print(ds)

    print("\nDIMENSIONS")
    print(dict(ds.sizes))

    print("\nVARIABLES")
    for name, variable in ds.data_vars.items():
        print(
            f"{name}: dimensions={variable.dims}, "
            f"shape={variable.shape}, units={variable.attrs.get('units', 'unknown')}"
        )

    print("\nCOORDINATES")
    for name, coordinate in ds.coords.items():
        print(f"{name}: size={coordinate.size}")
