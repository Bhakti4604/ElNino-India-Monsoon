
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOUNDARY_FILE = PROJECT_ROOT / "data" / "raw" / "india_boundary.geojson"

if not BOUNDARY_FILE.exists():
    raise FileNotFoundError(f"Boundary file not found: {BOUNDARY_FILE}")

boundary = gpd.read_file(BOUNDARY_FILE)

print("BOUNDARY VALIDATION")
print(f"Features: {len(boundary)}")
print(f"CRS: {boundary.crs}")
print(f"Geometry types: {boundary.geometry.geom_type.unique().tolist()}")
print(f"All geometries valid: {boundary.geometry.is_valid.all()}")
print(f"Empty geometries: {boundary.geometry.is_empty.sum()}")
print(f"Total bounds (min lon, min lat, max lon, max lat): {boundary.total_bounds}")
print(f"Columns: {boundary.columns.tolist()}")

if boundary.crs is None:
    raise ValueError("Boundary CRS is missing; cannot safely filter coordinates.")

boundary_wgs84 = boundary.to_crs("EPSG:4326")
print(f"WGS84 bounds: {boundary_wgs84.total_bounds}")
