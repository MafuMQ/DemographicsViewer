import dash
from dash import dcc, html, Output, Input
import dash_leaflet as dl
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json
import os

dataDict = {
    "ADM1": {"Shapefile": "geoBoundaries-ZAF-ADM1.shp", "CSV": "ADM1.csv"},
    "ADM2": {"Shapefile": "geoBoundaries-ZAF-ADM2.shp", "CSV": "ADM2.csv"},
    "ADM3": {"Shapefile": "geoBoundaries-ZAF-ADM3.shp", "CSV": "ADM3.csv"},
    "ADM4": {"Shapefile": "geoBoundaries-ZAF-ADM4.shp", "CSV": "ADM4.csv"},
}

def load_data(level):
    key = f"ADM{level}"
    shapefile = os.path.join("boundaries", dataDict[key]["Shapefile"])
    csvfile = dataDict[key]["CSV"]
    gdf = gpd.read_file(shapefile)
    df = pd.read_csv(csvfile)
    merged = gdf.merge(df, left_on='shapeName', right_on='region_id')
    return merged

def get_center(gdf):
    centroid = gdf.geometry.union_all().centroid
    return [centroid.y, centroid.x]

def geojson_features(gdf):
    features = []
    for _, row in gdf.iterrows():
        features.append({
            "type": "Feature",
            "geometry": row['geometry'].__geo_interface__,
            "properties": {
                "region_id": row['region_id'],
                "value1": row.get('value1', 0),
                "value2": row.get('value2', 0)
            }
        })
    return {"type": "FeatureCollection", "features": features}

def make_popup(region_id, value1, value2):
    fig = px.bar(
        x=['value1', 'value2'],
        y=[value1, value2],
        labels={'x': 'Metric', 'y': 'Value'},
        title=f"Data for {region_id}"
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Demographics Viewer"),
    dcc.Dropdown(
        id='level-dropdown',
        options=[{'label': f'ADM{l}', 'value': l} for l in range(1, 5)],
        value=1,
        clearable=False
    ),
    dl.Map(
        id="map",
        center=[-29, 24], #Default for south africa
        zoom=5,
        style={'width': '100%', 'height': '600px'},
        children=[
            dl.TileLayer(),
            dl.GeoJSON(
                id="geojson",
                options=dict(style=dict(weight=2, color="blue", fillOpacity=0.2)),
                hoverStyle=dict(weight=4, color='red', fillOpacity=0.5),
                zoomToBoundsOnClick=True
            )  # Always present!
        ]
    ),
    html.Div(id='popup-div')
])

@app.callback(
    Output("geojson", "data"),
    Output("map", "center"),
    Input("level-dropdown", "value")
)
def update_map(level):
    gdf = load_data(level)
    center = get_center(gdf)
    geojson = geojson_features(gdf)
    return geojson, center

@app.callback(
    Output('popup-div', 'children'),
    Input('geojson', 'featureClick'),
    Input('level-dropdown', 'value')
)
def display_popup(feature_click, level):
    print("feature_click:", feature_click)  # Debug print
    if not feature_click:
        return ""
    props = feature_click.get('properties', {})
    popup_html = make_popup(
        props.get('region_id', 'Unknown'),
        props.get('value1', 0),
        props.get('value2', 0)
    )
    return html.Iframe(srcDoc=popup_html, width="500", height="350")

if __name__ == '__main__':
    app.run(debug=True)