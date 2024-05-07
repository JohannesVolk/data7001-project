import pandas as pd
import os
import json
import pytz

def safe_json_loads(x):
    """Safely load JSON data, replacing single quotes with double quotes."""
    try:
        return json.loads(x.replace("'", "\""))
    except json.JSONDecodeError:
        return []

def extract_arrival_delay(upcoming_stops):
    """Extract 'arrival_delay' from the first dictionary in the list if available and properly structured."""
    if upcoming_stops and isinstance(upcoming_stops, list) and len(upcoming_stops) > 0:
        first_item = upcoming_stops[0]
        if isinstance(first_item, dict) and 'arrival_delay' in first_item:
            return first_item['arrival_delay']
    return None

def clean_csv_files(folder_path):
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

            # Ensure all desired columns are present, fill missing ones with None
            for col in desired_columns:
                if col not in df.columns:
                    df[col] = None

            # Handle JSON in 'upcoming_stops' and extract 'arrival_delay'
            df['upcoming_stops'] = df['upcoming_stops'].apply(lambda x: safe_json_loads(x) if pd.notnull(x) else [])
            df['arrival_delay'] = df['upcoming_stops'].apply(extract_arrival_delay)

            # Convert timestamps to Brisbane time
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
            df['timestamp'] = df['timestamp'].dt.tz_convert('Australia/Brisbane')

            df = df[desired_columns]

            df.to_csv(file_path, index=False)
            print(f"Processed and saved: {filename}")

folder_path = 'output/translink'
clean_csv_files(folder_path)
