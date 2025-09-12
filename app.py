import dash
from dash import dcc, html, Output, Input
import dash_leaflet as dl
import geopandas as gpd
import pandas as pd
import plotly.express as px
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
        center=[-29, 24],  # Default for South Africa
        zoom=5,
        style={'width': '100%', 'height': '600px'},
        children=[
            dl.TileLayer(),
            dl.GeoJSON(
                id="geojson",
                options=dict(style=dict(weight=2, color="blue", fillOpacity=0.2)),
                hoverStyle=dict(weight=4, color='red', fillOpacity=0.5),
                zoomToBoundsOnClick=True
            )
        ]
    ),
    html.Div(id="region-panel", style={"margin": "20px 0", "padding": "10px", "border": "1px solid #ccc"}),
    html.H2("Region Data"),
    dcc.Graph(id='region-graph')  # Graph appears here
])

# Update map polygons when level changes
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

# Update graph and panel when a polygon is clicked
@app.callback(
    Output('region-graph', 'figure'),
    Output('region-panel', 'children'),
    Input('geojson', 'clickData'),   # <-- change here
    Input('geojson', 'n_clicks'),
    Input('level-dropdown', 'value')
)
def display_graph_and_panel(clickData, n_clicks, level):
    if not clickData:
        return px.bar(title="Click a region to see data"), "Click a region to see details."
    # Extract properties as in test.py
    props = None
    if isinstance(clickData, dict):
        if "feature" in clickData and isinstance(clickData["feature"], dict):
            props = clickData["feature"].get("properties")
        elif "properties" in clickData and isinstance(clickData["properties"], dict):
            props = clickData["properties"]
        elif "payload" in clickData and isinstance(clickData["payload"], dict):
            payload = clickData["payload"]
            props = payload.get("properties") or (payload.get("feature") or {}).get("properties")
        elif "features" in clickData and isinstance(clickData["features"], list) and clickData["features"]:
            props = clickData["features"][0].get("properties")
    if not props:
        return px.bar(title="No data"), "No properties found in clickData."
    fig = px.bar(
        x=['value1', 'value2'],
        y=[props.get('value1', 0), props.get('value2', 0)],
        labels={'x': 'Metric', 'y': 'Value'},
        title=f"Data for {props.get('region_id', 'Unknown')}"
    )
    panel = html.Div([
        html.H3(f"Region: {props.get('region_id', 'Unknown')}"),
        html.P(f"Value 1: {props.get('value1', 0)}"),
        html.P(f"Value 2: {props.get('value2', 0)}"),
    ])
    return fig, panel

if __name__ == '__main__':
    app.run(debug=True)
