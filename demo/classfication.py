import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import numpy as np

def safe_json_loads(x):
    try:
        return json.loads(x.replace("'", "\""))
    except json.JSONDecodeError:
        return []

def load_and_combine_csv(folder_path):
    all_files = Path(folder_path).glob('*.csv')
    df_list = []
    for csv_file in all_files:
        df = pd.read_csv(csv_file, index_col=None, header=0)
        df['upcoming_stops'] = df['upcoming_stops'].apply(
            lambda x: safe_json_loads(x) if pd.notnull(x) else []
        )
        # Safely extract arrival_delay
        df['arrival_delay'] = df['upcoming_stops'].apply(
            lambda x: x[0].get('arrival_delay') if len(x) > 0 else None
        )
        df_list.append(df)
    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    return combined_df

def extract_arrival_delay(upcoming_stops):
    if upcoming_stops:
        # Check if the first item is a dictionary and has the 'arrival_delay' key
        if isinstance(upcoming_stops[0], dict) and 'arrival_delay' in upcoming_stops[0]:
            return upcoming_stops[0].get('arrival_delay')
    return None

df['arrival_delay'] = df['upcoming_stops'].apply(extract_arrival_delay)

def preprocess_data(df):
    # Convert timestamps to datetime objects and extract features
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['hour'] = df['timestamp'].dt.hour

    # Encode categorical variables
    label_encoders = {}
    for column in ['route_id_x', 'trip_id', 'vehicle_label', 'route_type']:
        label_encoders[column] = LabelEncoder()
        df[column] = label_encoders[column].fit_transform(df[column])

    # Handle missing arrival_delay
    df['arrival_delay'] = df['arrival_delay'].fillna(0)

    # Select features and target variable for classification
    features = df[['hour', 'lat', 'lon', 'route_type', 'stop_lat', 'stop_lon']]
    target = np.where(df['arrival_delay'] > 0, 1, 0)  # 1 for delay, 0 for no delay

    return features, target

# Function to scale features
def scale_features(features):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    return features_scaled

# Main script
if __name__ == "__main__":
    folder_path = 'output/translink'  # Path from content root
    df = load_and_combine_csv(folder_path)

    # Preprocess the data
    features, target = preprocess_data(df)

    # Scale the features
    features_scaled = scale_features(features)

    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(features_scaled, target, test_size=0.2, random_state=42)

    # Initialize the classifier
    classifier = RandomForestClassifier(random_state=42)

    # Train the classifier
    classifier.fit(X_train, y_train)

    # Predict on test data
    y_pred = classifier.predict(X_test)

    # Evaluate the classifier
    print(f"Classification Report:\n{classification_report(y_test, y_pred)}")
    print(f"Accuracy Score: {accuracy_score(y_test, y_pred)}")
