import os
import json
import http.server
from urllib.parse import urlparse
from datetime import datetime

# Data staging directory
data_directory = "/home/pi/air-quality/data/staging"

# Create the directory if it doesn't exist
if not os.path.exists(data_directory):
    os.makedirs(data_directory)


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
        if len(url_path_parts) > 3:
            filename_prefix = url_path_parts[3]
        else:
            filename_prefix = url_path_parts[1]

        # Generate a filename with the relevant prefix and datetime
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = os.path.join(data_directory, f"{filename_prefix}_{current_datetime}.json")

        # Save JSON data to the file
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)

        self._send_response(200, "JSON data saved successfully")


if __name__ == "__main__":
    port = 8080
    server_address = ('', port)

    httpd = http.server.HTTPServer(server_address, JSONRequestHandler)

    print(f"Server running on port {port}")
    httpd.serve_forever()
