import geopandas as gpd
import folium
import json
import os
import pandas as pd
import plotly.express as px
from folium import IFrame


def load_shapefile(path, filename):
    # Path to the shapefile
    shapefile_path = os.path.join(path, filename)

    # Load the shapefile with geopandas
    gdf = gpd.read_file(shapefile_path)
    print(gdf)
    return gdf

def load_csv_data(path):
    # Path to the CSV file (update as needed)
    csv_path = path  # Make sure this file exists and matches region IDs

    # Load the CSV data
    data_df = pd.read_csv(csv_path)
    return data_df

def merge_data(gdf, data_df):
    # Merge the GeoDataFrame with the CSV data on a common key (update 'region_id' as needed)
    # Replace 'region_id' with the actual column name in your shapefile and CSV
    merged_gdf = gdf.merge(data_df, left_on='shapeName', right_on='region_id')
    return merged_gdf

def create_map(merged_gdf):
    # Get the centroid of all geometries for map centering
    centroid = merged_gdf.geometry.union_all().centroid
    lat, lon = centroid.y, centroid.x

    m = folium.Map(location=[lat, lon], zoom_start=5)
    return m

# Function to create a Plotly chart and return HTML
def plotly_popup(row):
    # Example: create a bar chart for the region's data
    # Replace 'value1', 'value2' with actual data columns
    fig = px.bar(x=['value1', 'value2'], y=[row['value1'], row['value2']], labels={'x': 'Metric', 'y': 'Value'}, title=f"Data for {row['region_id']}")
    html = fig.to_html(include_plotlyjs='cdn', full_html=False)
    return html

# Add each region as a GeoJson with a popup
merged_gdf = merge_data(load_shapefile("boundaries","geoBoundaries-ZAF-ADM4.shp"), load_csv_data("data.csv"))
m = create_map(merged_gdf)

for _, row in merged_gdf.iterrows():
    geo_json = folium.GeoJson(row['geometry'].__geo_interface__)
    popup_html = plotly_popup(row)
    iframe = IFrame(popup_html, width="500", height="350")
    popup = folium.Popup(iframe, max_width=650)
    geo_json.add_child(popup)
    geo_json.add_to(m)

# Save the map to an HTML file
m.save("interactive_map.html")


