import geopandas as gpd
import folium
import json
import os

# Path to the shapefile
shapefile_path = os.path.join("boundaries", "geoBoundaries-ZAF-ADM4.shp")

# Load the shapefile with geopandas
gdf = gpd.read_file(shapefile_path)

# Get the centroid of all geometries for map centering
centroid = gdf.geometry.union_all().centroid
lat, lon = centroid.y, centroid.x

m = folium.Map(location=[lat, lon], zoom_start=5)

# Add the GeoDataFrame as a GeoJson layer
folium.GeoJson(gdf).add_to(m)

# Save the map to an HTML file
m.save("interactive_map.html")


