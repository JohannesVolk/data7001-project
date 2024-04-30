import json
from collections import defaultdict
import numpy as np
import csv 

# Load the JSON file again
file_path = 'qld_localities.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# Function to calculate the centroid of a polygon
def calculate_centroid(coordinates):
    # Flatten the list of coordinates and separate x and y
    coords = np.array(coordinates[0])  # Assuming polygons without holes
    x = coords[:, 0]
    y = coords[:, 1]
    # Calculate the centroid
    centroid_x = np.mean(x)
    centroid_y = np.mean(y)
    return (centroid_x, centroid_y)

# Dictionary to store features by their location name
features_by_name = defaultdict(list)

# Populate the dictionary with features
for feature in data["features"]:
    loc_name = feature["properties"]["LOC_NAME"]
    features_by_name[loc_name].append(feature)

# Filter out unique locations and calculate centroids for duplicates
# Prepare the data for the CSV by including individual centroids
duplicates_individual_info = []

for name, features in features_by_name.items():
    if len(features) > 1:  # Only consider names with more than one entry (duplicates)
        for feature in features:
            centroid = calculate_centroid(feature["geometry"]["coordinates"])
            duplicates_individual_info.append({
                "LOC_NAME": name,
                "LOC_PID": feature["properties"]["LOC_PID"],
                "Centroid_X": centroid[0],
                "Centroid_Y": centroid[1]
            })

# Update the CSV with Google Maps links for each centroid
csv_file_path_with_links = 'duplicates_individual_info_with_links.csv'

with open(csv_file_path_with_links, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(['LOC_NAME', 'LOC_PID', 'Centroid_X', 'Centroid_Y', 'Google_Maps_Link'])
    # Writing the data rows with Google Maps links
    for entry in duplicates_individual_info:
        maps_link = f"https://www.google.com/maps?q={entry['Centroid_Y']},{entry['Centroid_X']}"
        writer.writerow([
            entry['LOC_NAME'], 
            entry['LOC_PID'], 
            entry['Centroid_X'], 
            entry['Centroid_Y'],
            maps_link
        ])
