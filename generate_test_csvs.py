import geopandas as gpd
import pandas as pd

levels = [1, 2, 3]
for level in levels:
    shp_path = f"boundaries/geoBoundaries-ZAF-ADM{level}.shp"
    gdf = gpd.read_file(shp_path)
    # Get first 3 shapeNames
    shape_names = gdf['shapeName'].head(3).tolist()
    # Create test data
    df = pd.DataFrame({
        'region_id': shape_names,
        'value1': [10 * level + i for i in range(3)],
        'value2': [20 * level + i for i in range(3)],
    })
    df.to_csv(f"ADM{level}.csv", index=False)
print("Test CSVs for ADM1, ADM2, ADM3 created.")