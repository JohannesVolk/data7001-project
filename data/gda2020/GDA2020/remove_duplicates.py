import pandas as pd
import json

# Load the CSV file
csv_file_path = 'duplicates_info.csv'  # Modify this path to your CSV file
csv_data = pd.read_csv(csv_file_path)

# Extract LOC_PID values where 'Suburb Name in Brisbane' is 1 and 'Location in Brisbane' is "No"
loc_pids_to_remove = csv_data[(csv_data['Suburb Name in Brisbane'] == 1) & 
                              (csv_data['Location in Brisbane'] == 'No')]['LOC_PID'].tolist()

# Load the JSON file
json_file_path = 'qld_localities.json'  # Modify this path to your JSON file
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Filter the JSON features to exclude features with LOC_PID in the list
filtered_features = [feature for feature in json_data['features'] if feature['properties']['LOC_PID'] not in loc_pids_to_remove]

# Update the JSON data with filtered features
filtered_json_data = {
    "type": json_data['type'],
    "crs": json_data['crs'],
    "features": filtered_features
}

# Save the filtered JSON data to a new file
output_json_file_path = 'qld_localities_filtered.json'  # Modify this path to where you want to save the file
with open(output_json_file_path, 'w') as outfile:
    json.dump(filtered_json_data, outfile)

# Print the number of features before and after filtering
original_count = len(json_data['features'])
filtered_count = len(filtered_json_data['features'])
print(f'Original feature count: {original_count}, Filtered feature count: {filtered_count}')