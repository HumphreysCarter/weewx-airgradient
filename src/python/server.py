import os
import json
import pandas as pd
import http.server
from urllib.parse import urlparse
from datetime import datetime

# Data staging directory
api_directory = "/home/pi/air-quality/data/api/"
archive_directory = "/home/pi/air-quality/data/archive/"

# Create the directory if it doesn't exist
if not os.path.exists(api_directory):
    os.makedirs(api_directory)
if not os.path.exists(archive_directory):
    os.makedirs(archive_directory)

class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            json_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_response(400, "Invalid JSON data")
            return

        # Extract the relevant part of the URL path
        url_path = urlparse(self.path).path
        url_path_parts = url_path.split('/')
        serial_number = url_path_parts[3][url_path_parts[3].rfind(':')+1:]
        print(f'Reading data from AirGradient sensor {serial_number}')

        # Add datetime and serial number to entry
        json_data['serial'] = serial_number
        json_data['datetime'] = datetime.utcnow().isoformat()

        # Save json data to API file
        print(f'Saving JSON data for {serial_number}')
        with open(f'{api_directory}/AirGradient_{serial_number}.json', 'w') as f:
            json.dump(json_data, f, indent=2)

        # Export to archive
        print(f'Adding data for {serial_number} to archive')
        self.archive_data(serial_number, json_data)

        # Send response
        self._send_response(200, f"AirGradient sensor {serial_number} data saved successfully")

    def archive_data(self, serial_number, json_data):
        """
        Archives data for the AirGradient sensor to a csv file
        :param serial_number:
        :param json_data:
        :return:
        """
        json_data = json.dumps(json_data)
        new_data = pd.DataFrame([pd.read_json(json_data, typ='series')])

        # Create a CSV file for each serial number
        output_csv_path = os.path.join(archive_directory, f'AirGradient_{serial_number}.csv')

        try:
            data_archive = pd.read_csv(output_csv_path)
            output_df = pd.concat([data_archive, new_data], ignore_index=True)
            output_df.sort_values(by='datetime', inplace=True)
        except FileNotFoundError:
            output_df = new_data

        output_df.to_csv(output_csv_path, index=False)

if __name__ == "__main__":
    port = 8080
    server_address = ('', port)

    httpd = http.server.HTTPServer(server_address, JSONRequestHandler)

    print(f"Starting AirGradient data server on port {port}")
    httpd.serve_forever()
