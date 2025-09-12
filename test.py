import dash
from dash import html
import dash_leaflet as dl

app = dash.Dash(__name__)

app.layout = html.Div([
    dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(
            id="geojson",
            data={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[24, -29], [25, -29], [25, -28], [24, -28], [24, -29]]]
                        },
                        "properties": {"region_id": "test", "value1": 1, "value2": 2}
                    }
                ]
            },
            options=dict(style=dict(weight=2, color="blue", fillOpacity=0.2)),
            hoverStyle=dict(weight=4, color='red', fillOpacity=0.5),
            zoomToBoundsOnClick=True
        )
    ], style={'width': '100%', 'height': '600px'}, center=[-28.5, 24.5], zoom=7),
    html.Div(id='popup-div')
])

@app.callback(
    dash.Output('popup-div', 'children'),
    dash.Input('geojson', 'featureClick')
)
def display_popup(feature_click):
    print("feature_click:", feature_click)
    if not feature_click:
        return ""
    props = feature_click.get('properties', {})
    return str(props)

if __name__ == '__main__':
    app.run(debug=True)