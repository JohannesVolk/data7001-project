import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import json

def safe_json_loads(x):
    try:
        if pd.isnull(x):
            return {} 
        return json.loads(x.replace("'", "\""))
    except json.JSONDecodeError:
        print("Failed to decode JSON:", x)  # 输出解码失败的JSON
        return {}

def load_and_combine_csv(folder_path):
    all_files = Path(folder_path).glob('*.csv')
    df_list = []
    for csv_file in all_files:
        df = pd.read_csv(csv_file, index_col=None, header=0)
        df['upcoming_stops'] = df['upcoming_stops'].apply(lambda x: safe_json_loads(x) if pd.notnull(x) else {})
        df_list.append(df)
    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    return combined_df

def extract_arrival_delay(upcoming_stops):
    """Extract 'arrival_delay' from the dictionary if available and properly structured."""
    if isinstance(upcoming_stops, dict) and 'arrival_delay' in upcoming_stops:
        return 1 if upcoming_stops['arrival_delay'] > 0 else 0
    return 0

def preprocess_data(df, start_time, end_time):
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Australia/Brisbane')
    df = df[df['timestamp'].dt.time.between(pd.to_datetime(start_time).time(), pd.to_datetime(end_time).time())]
    df['is_delayed'] = df['upcoming_stops'].apply(extract_arrival_delay)
    df['rain_condition'] = (df['rain_dbz'] >= 20).astype(int)  # 添加降雨特征
    features = df[['timestamp']].copy()
    features['hour'] = df['timestamp'].dt.hour
    features['day_of_week'] = df['timestamp'].dt.dayofweek
    features['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6]).astype(int)
    features['rain_condition'] = df['rain_condition']  # 将降雨特征添加到特征矩阵中
    target = df['is_delayed']
    return features[['hour', 'day_of_week', 'is_weekend', 'rain_condition']], target


def run_classification(start_time, end_time, folder_path):
    df = load_and_combine_csv(folder_path)
    features, target = preprocess_data(df, start_time, end_time)
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.3, random_state=42)
    classifier = RandomForestClassifier(random_state=42, class_weight='balanced')
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)
    print(f"Classification report for {start_time} to {end_time}:")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy Score: {accuracy_score(y_test, y_pred)}")

folder_path = 'output/translink'

time_periods = [
    ("07:00:00", "09:00:00"),
    ("11:00:00", "13:00:00"),
    ("16:00:00", "18:00:00")
]

for start_time, end_time in time_periods:
    print(f"Running classification from {start_time} to {end_time}:")
    run_classification(start_time, end_time, folder_path)
