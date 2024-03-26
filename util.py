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
from collections import defaultdict
from dash.dependencies import Input, Output



def filter_lat_lon(df):
    df = df.loc[df["lat"] != 0]
    df = df.loc[df["lon"] != 0]
    return df

def get_route_updates():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get('https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates')
    feed.ParseFromString(response.content)

    features = defaultdict(list)

    for entity in feed.entity:
        l = []
        
        for i, upcoming_stop in enumerate(entity.trip_update.stop_time_update):
            if i == 1:
                break
            l += [{"stop_sequence": upcoming_stop.stop_sequence,"stop_id":upcoming_stop.stop_id, "arrival_time":upcoming_stop.arrival.time, "arrival_delay": upcoming_stop.arrival.delay}]

        features["trip_id"] += [entity.trip_update.trip.trip_id]
        features["route_id"] += [entity.trip_update.trip.route_id]
        features["upcoming_stops"] += [pd.DataFrame(l)]

    df = pd.DataFrame(data=features)
    return df
    
# get_updates()

def get_rt_vehicle_df():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get('https://gtfsrt.api.translink.com.au/api/realtime/SEQ/VehiclePositions')
    feed.ParseFromString(response.content)


    features = defaultdict(list)
    
    for entity in feed.entity:
        # print(entity)
        features["route_id"] += [entity.vehicle.trip.route_id]
        features["trip_id"] += [entity.vehicle.trip.trip_id]
        features["lat"] += [entity.vehicle.position.latitude]
        features["lon"] += [entity.vehicle.position.longitude]
        features["vehicle_label"] += [entity.vehicle.vehicle.label]
        features["vehicle_id"] += [entity.vehicle.vehicle.id]
        features["stop_id"] += [str(entity.vehicle.stop_id)]
        features["current_status"] += [entity.vehicle.current_status]
        features["timestamp"] += [entity.vehicle.timestamp]

    df = pd.DataFrame(data=features)
    return df

def get_df_connections(df_stops, df_rt):
    
    df = df_rt.merge(df_stops, on = "stop_id", suffixes=('_vehicle', '_stop'))

    # print(df)
    
    return df