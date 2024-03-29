from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import csv
from dash.dependencies import Input, Output

from util import *

# code and plot setup
# settings
pd.options.plotting.backend = "plotly"


app = JupyterDash(__name__)
app.layout = html.Div(
    [
        html.H1("Live Translink"),
        dcc.Interval(
            id="interval-component",
            interval=20 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        dcc.Graph(id="graph"),
        dcc.Input(
            id="input",
        ),
    ]
)

df_stops = pd.read_csv("stops.txt")
df_routes = pd.read_csv("routes.txt")


# Define callback to update graph
@app.callback(
    Output("graph", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("input", "value"),
    ],
)
def streamFig(value, input):
    df = get_rt_vehicle_df()

    df_combine = df.merge(df_routes, on="route_id")
    df_combine = df_combine.merge(df_stops, on="stop_id")

    df_combine = filter_lat_lon(df_combine)

    fig = go.Figure()

    if input != None:
        df_route_updates = get_route_updates()

        df_selection = df_combine.loc[df_combine["route_short_name"] == input]

        df_selection = df_selection.merge(df_route_updates, on="trip_id")

        # scatter live vehicle location
        fig.add_scattermapbox(
            mode="markers",
            lat=df_selection["lat"],
            lon=df_selection["lon"],
            marker=dict(size=16),
            text=df_selection["route_long_name"] + " to: " + df_selection["stop_name"],
        )

        # scatter upcoming stops for selected route
        for row in df_selection.iterrows():
            upcoming_stops = row[1]["upcoming_stops"].merge(df_stops, on="stop_id")

            fig.add_scattermapbox(
                mode="lines+markers",
                lat=upcoming_stops["stop_lat"],
                lon=upcoming_stops["stop_lon"],
                marker=dict(size=13),
                text=upcoming_stops["stop_name"]
                + " delay: "
                + str(upcoming_stops["arrival_delay"]),
            )

        fig.update_mapboxes(
            center={
                "lat": df_selection["lat"].mean(),
                "lon": df_selection["lon"].mean(),
            },
            zoom=11,
        )

    else:
        fig.add_scattermapbox(
            lat=df_combine["lat"],
            lon=df_combine["lon"],
            text=df_combine["route_short_name"]
            + " | "
            + df_combine["route_long_name"]
            + " to: "
            + df_combine["stop_name"],
        )
        fig.update_mapboxes(
            center={"lat": df_combine["lat"].mean(), "lon": df_combine["lon"].mean()},
            zoom=11,
        )

    df_combine.to_csv("debug_df.csv")

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


app.run_server(
    mode="external",
    port=8069,
    dev_tools_ui=True,  # debug=True,
    dev_tools_hot_reload=True,
    threaded=True,
)
