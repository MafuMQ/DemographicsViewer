import json
import dash
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[24, -29], [25, -29], [25, -28], [24, -28], [24, -29]]
                ]
            },
            "properties": {"region_id": "test", "value1": 1, "value2": 2}
        }
    ]
}

app.layout = html.Div([
    html.Div(
        dl.Map(
            children=[
                dl.TileLayer(),
                dl.GeoJSON(
                    id="geojson",
                    data=GEOJSON,
                    options=dict(style=dict(weight=2, color="blue", fillOpacity=0.2)),
                    hoverStyle=dict(weight=4, color='red', fillOpacity=0.5),
                    zoomToBoundsOnClick=True
                )
            ],
            style={'width': '100%', 'height': '600px'},
            center=[-28.5, 24.5],
            zoom=7,
            preferCanvas=False  # ensure SVG rendering so feature clicks are reliable
        ),
        style={"width": "70%", "display": "inline-block", "verticalAlign": "top"}
    ),

    html.Div([
        html.H3("Feature Info"),
        # We'll write either a table or the raw JSON here
        html.Div(id="info-panel", style={
            "border": "1px solid #ccc",
            "padding": "10px",
            "minHeight": "200px",
            "background": "#f9f9f9",
            "whiteSpace": "pre-wrap",
        })
    ], style={"width": "28%", "display": "inline-block", "marginLeft": "2%", "verticalAlign": "top"})
])


@app.callback(
    Output("info-panel", "children"),
    Input("geojson", "n_clicks"),           # triggers on every click
    State("geojson", "clickData"),         # stores the event payload (modern versions)
    prevent_initial_call=True
)
def display_info(n_clicks, clickData):
    # DEBUG: always print to server console so you can inspect what the component actually sent
    print("DEBUG: n_clicks =", n_clicks)
    print("DEBUG: clickData =", json.dumps(clickData, indent=2))

    if not clickData:
        return "Clicked, but no event data (clickData) was available. See server console for debugging."

    # attempt to find the feature properties in several possible payload shapes:
    props = None
    if isinstance(clickData, dict):
        # common patterns:
        if "feature" in clickData and isinstance(clickData["feature"], dict):
            props = clickData["feature"].get("properties")
        elif "properties" in clickData and isinstance(clickData["properties"], dict):
            props = clickData["properties"]
        elif "payload" in clickData and isinstance(clickData["payload"], dict):
            payload = clickData["payload"]
            # payload may contain 'feature' or 'properties'
            props = payload.get("properties") or (payload.get("feature") or {}).get("properties")
        elif "features" in clickData and isinstance(clickData["features"], list) and clickData["features"]:
            props = clickData["features"][0].get("properties")

    if props:
        rows = [html.Tr([html.Th("Property"), html.Th("Value")])]
        rows += [html.Tr([html.Td(k), html.Td(str(v))]) for k, v in props.items()]
        return html.Table(rows, style={"borderCollapse": "collapse", "width": "100%", "border": "1px solid #ccc"})
    else:
        # If we couldn't extract properties, show the entire clickData payload so we can debug
        return html.Pre(json.dumps(clickData, indent=2))


if __name__ == "__main__":
    app.run(debug=True)
