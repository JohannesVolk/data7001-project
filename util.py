from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path
from osgeo import gdal
import time
import rasterio
import matplotlib.pyplot as plt
import cv2
from matplotlib.colors import hex2color, rgb2hex


def get_radar_value_lonlat_time(lon, lat, meta, image):
    # print(f"output/weather/radar_{timestamp}.tif")

    # Use the transform in the metadata and your coordinates
    rowcol = rasterio.transform.rowcol(meta["transform"], xs=lon, ys=lat)

    value = image[:, *rowcol]

    return rgb2hex(value.astype(np.float32) / 255, keep_alpha=True)


def filter_lat_lon(df):
    df = df.loc[df["lat"] != 0]
    df = df.loc[df["lon"] != 0]
    return df


def get_route_updates():
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(
        "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates"
    )
    feed.ParseFromString(response.content)

    features = defaultdict(list)

    for entity in feed.entity:
        l = []

        for i, upcoming_stop in enumerate(entity.trip_update.stop_time_update):
            if i == 1:
                break
            l = [
                {
                    "stop_sequence": upcoming_stop.stop_sequence,
                    "stop_id": upcoming_stop.stop_id,
                    "arrival_time": upcoming_stop.arrival.time,
                    "arrival_delay": upcoming_stop.arrival.delay,
                }
            ]

        if len(l) != 0:
            features["trip_id"] += [entity.trip_update.trip.trip_id]
            features["route_id"] += [entity.trip_update.trip.route_id]
            features["upcoming_stops"] += l
        
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

    df_stops = pd.read_csv("data/stops.txt")
    df_routes = pd.read_csv("data/routes.txt")

    path = Path(path)

    path.mkdir(parents=True, exist_ok=True)

    for iteration in range(iterations):
        # collect weather
        # weather updates every 10 minutes
        if iteration % (2 * 10) == 0:
            timestamp_radar = collect_weather(path / "weather")

        # collect live location translink vehicles
        t = time.perf_counter_ns()
        collect_translink(
            path / "translink", df_routes, df_stops, iteration, timestamp_radar
        )
        print(f"time took = {(time.perf_counter_ns() - t)/ 10e9}")

        # sleep until next poll
        time.sleep(time_interval)


def aggregate_csvs(path: Path = "output/"):
    df = None
    path = Path(path) / "translink"

    i = 0

    def read_messurement_df(path):
        df = csv_to_df(path)

        nonlocal i
        df.insert(0, "num_measurement", i)
        i += 1
        return df

    p = map(lambda x: read_messurement_df(x), path.iterdir())

    df = pd.concat(p)

    return df


import urllib.request
import json

'''
def collect_translink(path, df_routes, df_stops, iteration, timestamp_radar=0):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    df = get_rt_vehicle_df()

    df_combine = df.merge(df_routes, on="route_id")
    df_combine = df_combine.merge(df_stops, on="stop_id")

    df_combine = filter_lat_lon(df_combine)

    df_route_updates = get_route_updates()

    df_combine = df_combine.merge(df_route_updates, on="trip_id")

    df_combine.insert(0, "timestamp_radar", timestamp_radar)

    df_combine.to_csv(path / f"{iteration}.csv", index=False)
'''

def collect_translink(path, df_routes, df_stops, iteration, timestamp_radar=0):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    df = get_rt_vehicle_df()

    df_combine = df.merge(df_routes, on="route_id")
    df_combine = df_combine.merge(df_stops, on="stop_id")

    df_combine = filter_lat_lon(df_combine)

    df_route_updates = get_route_updates()

    df_combine = df_combine.merge(df_route_updates, on="trip_id")

    df_combine.insert(0, "timestamp_radar", timestamp_radar)

    # Get the current timestamp
    timestamp = time.time()

    # Save the data with the timestamp as the filename
    timestamp_str = str(int(timestamp))
    filename = f"{timestamp_str}.csv"
    df_combine.to_csv(path / filename, index=False)

def save_observation(type_, url_data, path, name):
    LAT, LON = -27.470125, 153.021072
    lon_ul, lat_ul = 151.875003, -27.059128
    lon_lr, lat_lr = 154.687502, -29.535232

    # url_complete = f"{url_data}{type_['path']}/{512}/{6}/{LAT}/{LON}/{4 if i == 0 else 0}/0_0.png"
    url_complete = f"{url_data}{type_['path']}/{512}/{7}/{118}/{74}/{0 if name == 'radar' else 0}/0_0.png"

    # color mapping at https://www.rainviewer.com/api/color-schemes.html
    urllib.request.urlretrieve(url_complete, path / f"{name}_{type_['time']}.jpg")

    ds = gdal.Open(path / f"{name}_{type_['time']}.jpg")

    coords_observation_grid = [lon_ul, lat_ul, lon_lr, lat_lr]

    ds = gdal.Translate(
        path / f"{name}_{type_['time']}.tif",
        ds,
        format="GTiff",
        outputSRS="EPSG:4326",
        outputBounds=coords_observation_grid,
    )


def collect_weather(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    url_json = "https://api.rainviewer.com/public/weather-maps.json"

    response = urllib.request.urlopen(url_json)

    # storing the JSON response
    # from url in data
    data_json = json.loads(response.read())

    url_data = "https://tilecache.rainviewer.com/"
    names = ["radar", "satellite"]
    for i, types_ in enumerate(
        [data_json["radar"]["nowcast"], data_json["satellite"]["infrared"]]
    ):
        for type_ in types_:
            save_observation(type_, url_data, path, names[i])

            if i == 0:
                timestamp_radar = type_["time"]

    return timestamp_radar


def csv_to_df(path):
    df = pd.read_csv(path)

    def func(x: str):
        x = x.replace("'", '"')
        res = json.loads(x)
        return pd.DataFrame(res, index=[0])

    df["upcoming_stops"] = df["upcoming_stops"].apply(func)

    rain_color_mapping = pd.read_csv("data/color_rain_mapping.csv")

    src = None
    meta = None
    image = None

    def func_rain_mapping(lon, lat, timestamp):
        nonlocal src, meta, image
        if src is None:
            src = rasterio.open(f"output/weather/radar_{timestamp}.tif")
            meta = src.meta
            image = src.read()

        color_at_lon_lat = get_radar_value_lonlat_time(lon, lat, meta, image)

        x = (
            rain_color_mapping[rain_color_mapping["BnW"] == color_at_lon_lat]["dBZ"]
            .iloc[0]
            .item()
        )

        return x

    col = df.apply(
        lambda x: func_rain_mapping(x["lon"], x["lat"], x["timestamp_radar"]), axis=1
    )

    df.insert(0, "rain_dbz", col)

    return df


import plotly.express as px

def delay_mapper(x):
    delays = x["arrival_delay"]
    delays.name = "delays"
    return delays

def get_delay_histogram(dataframe,  quantiles = [0, 1]):
    delays = dataframe["upcoming_stops"].apply(delay_mapper)
    delays.insert(0, "route_type", dataframe["route_type"])

    q_low = delays[0].quantile(quantiles[0])
    q_hi = delays[0].quantile(quantiles[1])
    delays = delays[(delays[0] <= q_hi) & (delays[0] >= q_low)]
    
    return px.histogram(delays, title="frame delay histogram", x=0, color="route_type", histnorm='probability density')


def get_rain_delay_plot(dataframe, quantiles = [0, 1]):
    delays = dataframe["upcoming_stops"].apply(delay_mapper)
    delays.insert(0, "rain_dbz", dataframe["rain_dbz"])
    delays.insert(0, "route_type", dataframe["route_type"])

    q_low = delays[0].quantile(quantiles[0])
    q_hi = delays[0].quantile(quantiles[1])
    delays = delays[(delays[0] <= q_hi) & (delays[0] >= q_low)]
    
    return px.scatter(delays, title="rain vs. delay", y=0, x="rain_dbz")#, color="route_type")

