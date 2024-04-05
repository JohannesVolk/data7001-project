import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import csv
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import matplotlib.pyplot as plt
import cv2


from util import *


LIVE = False

# code and plot setup
# settings
# pd.options.plotting.backend = "plotly"

paths_translink = list(Path("output/translink").iterdir())

app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.H1("Live Translink"),
        dcc.Interval(
            id="interval-component",
            interval=180 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="graph")),
                dbc.Col(
                    [
                        "Select route number: ",
                        dcc.Input(
                            id="input",
                        ),
                        dcc.Graph(id="graph2"),
                        dcc.Slider(
                            0,
                            len(paths_translink),
                            1,
                            value=0,
                            id="slider",
                            marks=None,
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row([dbc.Col(dcc.Graph(id="graph3")), dbc.Col(dcc.Graph(id="graph4")), dbc.Col(dcc.Graph(id="graph5"))]),
    ]
)

df_stops = pd.read_csv("data/stops.txt")
df_routes = pd.read_csv("data/routes.txt")



fig4, fig5 = None, None

# CAUTION might take a long time if a lot of data is collected in ./output
df_aggregate = aggregate_csvs()
quantiles = [0.05, 0.95]
fig4 = get_delay_histogram(df_aggregate, quantiles)
fig5 = get_rain_delay_plot(df_aggregate, quantiles)


# Define callback to update graph
@app.callback(
    [
        Output("graph", "figure"),
        Output("graph2", "figure"),
        Output("graph3", "figure"),
        Output("graph4", "figure"),
        Output("graph5", "figure"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("input", "value"),
        Input("slider", "value"),
    ],
)
def streamFig(value, input, slider):
    if LIVE:
        df = get_rt_vehicle_df()
        df_combine = df.merge(df_routes, on="route_id")
        df_combine = df_combine.merge(df_stops, on="stop_id")
        df_combine = filter_lat_lon(df_combine)
    else:
        df_combine = csv_to_df(paths_translink[slider])

    df_combine["rain_dbz"] = df_combine["rain_dbz"].astype(str)
    fig = go.Figure()

    if input != None:
        if LIVE:
            df_route_updates = get_route_updates()

        df_selection = df_combine.loc[df_combine["route_short_name"] == input]

        if LIVE:
            df_selection = df_selection.merge(df_route_updates, on="trip_id")

        # scatter live vehicle location
        fig.add_scattermapbox(
            mode="markers",
            lat=df_selection["lat"],
            lon=df_selection["lon"],
            marker=dict(size=16),
            name="vehicles",
            text=df_selection["vehicle_label"]
            + " | "
            + df_selection["route_long_name"]
            + " to: "
            + df_selection["stop_name"]
            + " rain: "
            + df_selection["rain_dbz"],
        )

        # scatter upcoming stops for selected route
        for row_num, row in enumerate(df_selection.iterrows()):
            upcoming_stops = row[1]["upcoming_stops"].merge(df_stops, on="stop_id")
            fig.add_scattermapbox(
                mode="lines+markers",
                lat=upcoming_stops["stop_lat"],
                lon=upcoming_stops["stop_lon"],
                name="vehicle " + row[1]["vehicle_label"] + " destination",
                marker=dict(size=13),
                text=upcoming_stops["stop_name"]
                + " delay: "
                + str(upcoming_stops["arrival_delay"].item()),
            )

        fig.update_mapboxes(
            center={
                "lat": df_selection["lat"].mean(),
                "lon": df_selection["lon"].mean(),
            },
            zoom=11,
        )

    else:
        route_type_mapper_dict = {"Tram":"yellow", "":"cyan", "Train":"green", "Bus":"tomato", "Boat":"aqua"}
        
        for route_type_name, df_by_route_type in df_combine.groupby("route_type"):
            fig.add_scattermapbox(
                lat=df_by_route_type["lat"],
                lon=df_by_route_type["lon"],
                name = route_type_name,
                fillcolor=route_type_mapper_dict[route_type_name],
                text=df_by_route_type["route_short_name"]
                + " | "
                + df_by_route_type["route_long_name"]
                + " to: "
                + df_by_route_type["stop_name"]
                + " rain: "
                + df_by_route_type["rain_dbz"],
            )
        fig.update_mapboxes(
            center={"lat": df_combine["lat"].mean(), "lon": df_combine["lon"].mean()},
            zoom=11,
        )

    # rain radar -----------------------------------------
    # print(f"output/weather/radar_{df_combine['timestamp_radar'].iloc[0].item()}.jpg")
    image = cv2.imread(
        f"output/weather/radar_{df_combine['timestamp_radar'].iloc[0].item()}.jpg"
    )[:, :, ::-1]

    image_base = cv2.imread("data/base_observationwindow.png")[:, :, ::-1]
    image_base = cv2.resize(image_base, (512, 512), interpolation=cv2.INTER_LINEAR)
    image = cv2.addWeighted(image_base, 0.3, image, 0.6, 0)
    fig2 = px.imshow(image[:300, 50:350, :], title="rain radar")

    # delay plots -----------------------------------------
    
    fig3 = get_delay_histogram(df_combine)
    # fig5 = get_rain_delay_plot(df_combine)

    # ----------------------------------------

    fig.update_layout(
        mapbox_style="open-street-map",
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig, fig2, fig3, fig4, fig5


app.run_server(
    mode="external",
    port=8069,
    dev_tools_ui=True,  # debug=True,
    dev_tools_hot_reload=True,
    threaded=True,
)
