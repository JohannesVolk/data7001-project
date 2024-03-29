from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path
from osgeo import gdal
import time


def filter_lat_lon(df):
    df = df.loc[df["lat"] != 0]
    df = df.loc[df["lon"] != 0]
    return df


def get_route_updates(num_stops_ahead=1):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(
        "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates"
    )
    feed.ParseFromString(response.content)

    features = defaultdict(list)

    for entity in feed.entity:
        l = []

        for i, upcoming_stop in enumerate(entity.trip_update.stop_time_update):
            if i == num_stops_ahead:
                break
            l += [
                {
                    "stop_sequence": upcoming_stop.stop_sequence,
                    "stop_id": upcoming_stop.stop_id,
                    "arrival_time": upcoming_stop.arrival.time,
                    "arrival_delay": upcoming_stop.arrival.delay,
                }
            ]

        features["trip_id"] += [entity.trip_update.trip.trip_id]
        features["route_id"] += [entity.trip_update.trip.route_id]
        features["upcoming_stops"] += [pd.DataFrame(l)]

    df = pd.DataFrame(data=features)
    return df


def get_rt_vehicle_df():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(
        "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/VehiclePositions"
    )
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


def collect_data(path="output", iterations=1, time_interval=1):
    """_summary_

    Args:
        path (str, optional): output path. Defaults to "output".
        iterations (int, optional): num of iterations to perform. Defaults to 1.
        time_interval (int, optional): time to wait between iteration in seconds. Defaults to 1.
    """

    df_stops = pd.read_csv("stops.txt")
    df_routes = pd.read_csv("routes.txt")

    path = Path(path)

    path.mkdir(parents=True, exist_ok=True)

    for iteration in range(iterations):
        # collect weather
        # only poll every 2.5 minutes (weather updates every 10 minutes regarless)
        if iteration % (time_interval * 60 * 2.5) == 0:
            collect_weather(path / "weather")
        
        
        # collect live location translink vehicles
        t = time.perf_counter_ns()
        collect_translink(path / "translink", df_routes, df_stops, iteration)
        print(f"time took = {(time.perf_counter_ns() - t)/ 10e9}")

        # sleep until next poll
        time.sleep(time_interval)


def aggregate_csvs(path: Path = "output/"):
    df = None
    path = Path(path)


    i = 0

    def read_messurement_df(path):
        df = pd.read_csv(path / "translink")
        
        nonlocal i

        df.insert(0, "num_measurement", i)
    
        i += 1
        return df

    p = map(lambda x: read_messurement_df(x), path.iterdir())
    
    df = pd.concat(p)

    print(df)



import urllib.request
import json

def collect_translink(path, df_routes, df_stops, iteration):
    df = get_rt_vehicle_df()

    df_combine = df.merge(df_routes, on="route_id")
    df_combine = df_combine.merge(df_stops, on="stop_id")

    df_combine = filter_lat_lon(df_combine)

    df_route_updates = get_route_updates()

    df_combine = df_combine.merge(df_route_updates, on="trip_id")

    df_combine.to_csv(path / f"{iteration}.csv", index=False)

def collect_weather(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    url_json = 'https://api.rainviewer.com/public/weather-maps.json'
    
    response = urllib.request.urlopen(url_json) 

    # storing the JSON response  
    # from url in data 
    data_json = json.loads(response.read()) 
    
    current_radar_meta = data_json["radar"]["nowcast"][0]
    current_satellite_meta = data_json["satellite"]["infrared"][0]
    coverage = "v2/coverage/0"
    
    url_data = "https://tilecache.rainviewer.com/"
    
    for i, type_ in enumerate([current_radar_meta, current_satellite_meta]):
        
        names = ["radar", "satellite"]
        
        LAT, LON = -27.470125, 153.021072
        lon_ul, lat_ul = 151.875003, -27.059128
        lon_lr, lat_lr = 154.687502, -29.535232
        
        # url_complete = f"{url_data}{type_['path']}/{512}/{6}/{LAT}/{LON}/{4 if i == 0 else 0}/0_0.png"
        url_complete = f"{url_data}{type_['path']}/{512}/{7}/{118}/{74}/{4 if i == 0 else 0}/0_0.png"

        print(url_complete)

        # color mapping at https://www.rainviewer.com/api/color-schemes.html
        urllib.request.urlretrieve(url_complete, path / f"{names[i]}_{type_['time']}.png")
        
        
        ds = gdal.Open(path / f"{names[i]}_{type_['time']}.png")
        
        coords_observation_grid = [lon_ul, lat_ul, lon_lr, lat_lr]
        
        ds = gdal.Translate(path / f"{names[i]}_{type_['time']}.tif", ds, format = 'GTiff', outputSRS = 'EPSG:4326', outputBounds = coords_observation_grid)
        print(ds)

