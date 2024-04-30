import json
import pandas as pd
import csv

# Load the JSON data
with open('qld_localities.json', 'r') as file:
    data = json.load(file)

# Extract the relevant columns
loc_names = [feature['properties']['LOC_NAME'] for feature in data['features']]
loc_pids = [feature['properties']['LOC_PID'] for feature in data['features']]

# Create the Pandas DataFrame
df = pd.DataFrame({
    'LOC_NAME': loc_names,
    'LOC_PID': loc_pids
})

# Check for duplicate LOC_NAME values
duplicate_loc_names = df['LOC_NAME'].value_counts()[df['LOC_NAME'].value_counts() > 1].index.tolist()

if duplicate_loc_names:
        
    print("LOC_PIDs for duplicate LOC_NAME values:")
    for loc_name in duplicate_loc_names:
        duplicate_loc_pids = df.loc[df['LOC_NAME'] == loc_name, 'LOC_PID'].tolist()
        print(f"{loc_name}, {', '.join(duplicate_loc_pids)}")
else:
    print("No duplicate LOC_NAME values found.")