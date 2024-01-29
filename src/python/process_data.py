import os
import pandas as pd
from datetime import datetime

# Directory paths
staging_directory = '/home/pi/air-quality/data/staging'
archive_directory = '/home/pi/air-quality/data/archive'

# List all JSON files in the staging directory
json_files = [f for f in os.listdir(staging_directory) if f.endswith('.json')]

# Iterate over each JSON file
for json_file in json_files:
    print(json_file)
    json_file_path = os.path.join(staging_directory, json_file)

    # Extract serial number and time from the file name
    file_name_parts = json_file.split('_')
    serial_number = file_name_parts[0].split(':')[-1]
    time_record = file_name_parts[1].split('.')[0]

    # Read JSON content into a DataFrame
    data = pd.DataFrame([pd.read_json(json_file_path, typ='series')])

    # Add serial number and time columns to the DataFrame
    data['serial'] = serial_number
    data['datetime'] = datetime.strptime(time_record, '%Y%m%d%H%M%S')
    data.sort_values(by='datetime', inplace=True)

    # Create a CSV file for each serial number
    output_csv_path = os.path.join(archive_directory, f'AirGradient_{serial_number}.csv')

    # Append the data to the CSV file
    try:
        data_archive = pd.read_csv(output_csv_path)
        output_df = pd.concat([data_archive, data], ignore_index=True)
    except FileNotFoundError:
        output_df = data

    output_df.to_csv(output_csv_path, index=False)

    # Delete the JSON file
    os.remove(json_file_path)

print('Operation completed successfully.')
