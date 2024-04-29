import pandas as pd
import os

folder_path = 'output/translink'

desired_columns = [
    'timestamp', 'route_id_x', 'trip_id', 'lat', 'lon', 'vehicle_label', 'vehicle_id', 'stop_id',
    'current_status', 'timestamp_radar', 'route_short_name', 'route_long_name', 'route_desc',
    'route_type', 'route_url', 'route_color', 'route_text_color', 'stop_code', 'stop_name',
    'stop_desc', 'stop_lat', 'stop_lon', 'zone_id', 'stop_url', 'location_type', 'parent_station',
    'platform_code', 'route_id_y', 'upcoming_stops'
]

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)

        for col in desired_columns:
            if col not in df.columns:
                df[col] = None

        df = df[desired_columns]

        df.to_csv(file_path, index=False)
        print(f"Processed and saved: {filename}")

