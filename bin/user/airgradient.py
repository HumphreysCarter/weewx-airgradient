# Copyright 2024 by Carter Humphreys <carter.humphreys@lake-effect.dev>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
WeeWX extension that records AirGradient air quality sensor readings.
"""

import sys
import json
import time
import weewx
import threading
import weewx.units
import urllib.request
from weewx.engine import StdService
from datetime import datetime

import logging

log = logging.getLogger(__name__)

# Check that system python version is >= 3.9
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 9):
    raise weewx.UnsupportedFeature(
        " weewx-airgradient requires Python 3.9 or later, found %s.%s" % (sys.version_info[0], sys.version_info[1]))

# Check that weewx version >= 5
if weewx.__version__ < "4":
    raise weewx.UnsupportedFeature(
        " weewx-airgradient requires WeeWX 4 or later, found %s" % weewx.__version__)

# Create initial database schema, other columns are created on the fly for each sensor.
schema = [
    ('dateTime', 'INTEGER NOT NULL PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
]


def get_value(data, key, min_value=None, max_value=None):
    try:
        value = data[key]

        if min_value is not None and value < min_value:
            return None

        if max_value is not None and value > max_value:
            return None

        return value
    except KeyError as e:
        return None


def get_sensor_data(sensor_serial):
    try:
        with urllib.request.urlopen(f'http://airgradient_{sensor_serial}.local/measures/current') as url:
            return json.load(url)

    except urllib.error.URLError as e:
        log.warning(f'AirGradient Ingest: Error getting data from sensor {sensor_serial}. {e}')
        return None


def pm02_to_aqi(pm02):
    if pm02 <= 9.0:
        return calculate_aqi_range(pm02, 0, 9.0, 0, 50)
    elif pm02 <= 35.4:
        return calculate_aqi_range(pm02, 9.1, 35.4, 51, 100)
    elif pm02 <= 55.4:
        return calculate_aqi_range(pm02, 35.5, 55.4, 101, 150)
    elif pm02 <= 125.4:
        return calculate_aqi_range(pm02, 55.5, 125.4, 151, 200)
    elif pm02 <= 225.4:
        return calculate_aqi_range(pm02, 125.5, 225.4, 201, 300)
    elif pm02 <= 325.4:
        return calculate_aqi_range(pm02, 225.5, 325.4, 301, 500)
    else:
        return 500


def pm10_to_aqi(pm10):
    if pm10 <= 54:
        return calculate_aqi_range(pm10, 0, 54, 0, 50)
    elif pm10 <= 154:
        return calculate_aqi_range(pm10, 55, 154, 51, 100)
    elif pm10 <= 254:
        return calculate_aqi_range(pm10, 155, 254, 101, 150)
    elif pm10 <= 354:
        return calculate_aqi_range(pm10, 255, 354, 151, 200)
    elif pm10 <= 424:
        return calculate_aqi_range(pm10, 355, 424, 201, 300)
    elif pm10 <= 504:
        return calculate_aqi_range(pm10, 425, 504, 301, 400)
    elif pm10 <= 604:
        return calculate_aqi_range(pm10, 505, 604, 401, 500)
    else:
        return 500


def calculate_aqi_range(C, Cl, Ch, Il, Ih):
    aqi = ((Ih - Il) / (Ch - Cl)) * (C - Cl) + Il
    return aqi


def calculate_nowcast(pm_measurements):
    """
    Methodology: https://usepa.servicenowservices.com/airnow/en/how-is-the-nowcast-algorithm-used-to-report-current-air-quality?id=kb_article_view&sys_id=bb8b65ef1b06bc10028420eae54bcb98&spa=1
    """
    try:
        # Step 1: Select the minimum and maximum PM measurements
        pm_min = min(pm_measurements)
        pm_max = max(pm_measurements)

        # Step 2: Subtract the minimum measurement from the maximum measurement to get the range
        pm_range = pm_max - pm_min

        # Step 3: Divide the range by the maximum measurement in the 12-hour period to get the scaled rate of change
        scaled_rate_change = pm_range / pm_max if pm_max != 0 else 0

        # Step 4: Subtract the scaled rate of change from 1 to get the weight factor
        weight_factor = 1 - scaled_rate_change

        # Step 5: Ensure the weight factor is between 0.5 and 1
        weight_factor = max(0.5, min(1, weight_factor))

        # Step 6: Multiply each hourly measurement by the weight factor raised to the power of the number of hours ago
        #         the value was measured
        nowcast_values = [measurement * weight_factor ** i for i, measurement in enumerate(pm_measurements)]

        # Step 7: Compute the NowCast by summing the products from Step 6 and dividing by the sum of the weight factor
        #         raised to the power of the number of hours ago each value was measured
        nowcast = sum(nowcast_values) / sum(weight_factor ** i for i in range(len(pm_measurements)))

        return nowcast
    except Exception as e:
        log.error(f'AirGradient Ingest: Error calculating NowCast AQI: {e}.')
        return None


class AirGradientDataIngest(StdService):

    def __init__(self, engine, config_dict):

        # Get user configuration from weewx.conf
        user_config = config_dict.get('AirGradient', {})
        binding = user_config['data_binding']
        self.max_age_seconds = int(user_config['max_age_seconds'])
        self.sensors = user_config['sensors']

        # Setup schema and units for database
        for sensor in self.sensors:
            log.debug(f'Setting up database schema and units for sensor {sensor}')

            # Create database schema for each sensor
            schema.append((f'airquality_{sensor}_pm02_aqi', 'REAL'))
            schema.append((f'airquality_{sensor}_pm10_aqi', 'REAL'))
            schema.append((f'airquality_{sensor}_pm02_nowcast', 'REAL'))
            schema.append((f'airquality_{sensor}_pm10_nowcast', 'REAL'))
            schema.append((f'airquality_{sensor}_pm01', 'INTEGER'))
            schema.append((f'airquality_{sensor}_pm02', 'INTEGER'))
            schema.append((f'airquality_{sensor}_pm10', 'INTEGER'))
            schema.append((f'airquality_{sensor}_pm003_count', 'INTEGER'))
            schema.append((f'airquality_{sensor}_atmp', 'REAL'))
            schema.append((f'airquality_{sensor}_atmp_compensated', 'REAL'))
            schema.append((f'airquality_{sensor}_rhum', 'INTEGER'))
            schema.append((f'airquality_{sensor}_rhum_compensated', 'INTEGER'))
            schema.append((f'airquality_{sensor}_rco2', 'INTEGER'))
            schema.append((f'airquality_{sensor}_tvoc_raw', 'INTEGER'))
            schema.append((f'airquality_{sensor}_tvoc_index', 'INTEGER'))
            schema.append((f'airquality_{sensor}_nox_raw', 'INTEGER'))
            schema.append((f'airquality_{sensor}_nox_index', 'INTEGER'))
            schema.append((f'airquality_{sensor}_wifi', 'INTEGER'))

            # assign units types
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm02_aqi'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm10_aqi'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm02_nowcast'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm10_nowcast'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm01'] = 'group_concentration'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm02'] = 'group_concentration'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm10'] = 'group_concentration'
            weewx.units.obs_group_dict[f'airquality_{sensor}_pm003_count'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_atmp'] = 'group_temperature'
            weewx.units.obs_group_dict[f'airquality_{sensor}_atmp_compensated'] = 'group_temperature'
            weewx.units.obs_group_dict[f'airquality_{sensor}_rhum'] = 'group_percent'
            weewx.units.obs_group_dict[f'airquality_{sensor}_rhum_compensated'] = 'group_percent'
            weewx.units.obs_group_dict[f'airquality_{sensor}_rco2'] = 'group_fraction'
            weewx.units.obs_group_dict[f'airquality_{sensor}_tvoc_raw'] = 'group_concentration'
            weewx.units.obs_group_dict[f'airquality_{sensor}_tvoc_index'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_nox_raw'] = 'group_concentration'
            weewx.units.obs_group_dict[f'airquality_{sensor}_nox_index'] = 'group_count'
            weewx.units.obs_group_dict[f'airquality_{sensor}_wifi'] = 'group_count'

        # Initialize superclass
        super(AirGradientDataIngest, self).__init__(engine, config_dict)

        # Create weewx database connection
        self.database_manager = self.engine.db_binder.get_manager(data_binding=binding, initialize=True)

        # Check that all sensors are within the database
        db_columns = self.database_manager.connection.columnsOf(self.database_manager.table_name)
        missing_columns = [column for column in schema if column[0] not in db_columns]
        for column_name, column_type in missing_columns:
            log.info(f'Adding column {column_name} with type {column_type} to database.')
            self.database_manager.add_column(column_name, column_type)

        # Listen for new archive records from weewx
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.save_record_to_database)

        # Start data collection thread
        self._thread = AirGradientDataThread(self.config_dict)
        self._thread.start()

    def shutdown(self):
        try:
            self.database_manager.close()
        except:
            pass

        if self._thread:
            self._thread.running = False
            self._thread.join()
            self._thread = None

    def save_record_to_database(self, event):
        """
        Saves AirGradient data to the database.
        """
        # Get datetime of weewx record
        record_dt = datetime.utcfromtimestamp(event.record['dateTime'])

        # Get AirGradient data record
        record = self._thread.get_record()

        # Add record to database
        if not record:
            log.info('AirGradient Ingest: Skipping record empty.')
        else:
            # Check if time delta close enough to record. Keeps current data from getting assigned to old data.
            delta = (datetime.utcnow() - record_dt).total_seconds()
            if delta > self.max_age_seconds:
                log.info(
                    f'AirGradient Ingest: Skipping record {datetime.fromtimestamp(event.record["dateTime"])} ({event.record["dateTime"]}). Record old.')
            else:
                # Add raw sensor data to database
                self.database_manager.addRecord(record)

                # Calculate both AQI and NowCast AQI for each sensor and update the record
                for sensor in self.sensors:
                    log.info(f"AirGradient Ingest: Calculating AQI and NowCast AQI for sensor {sensor}.")
                    try:
                        # Calculate AQI
                        pm02_aqi, pm10aqi = self.calculate_aqi(sensor, record['dateTime'])
                        self.database_manager.updateValue(record['dateTime'], f'airquality_{sensor}_pm02_aqi', pm02_aqi)
                        self.database_manager.updateValue(record['dateTime'], f'airquality_{sensor}_pm10_aqi', pm10aqi)

                        # Calculate NowCast AQI
                        pm02_nowcast, pm10_nowcast = self.calculate_nowcast_aqi(sensor, record['dateTime'])
                        self.database_manager.updateValue(record['dateTime'], f'airquality_{sensor}_pm02_nowcast',
                                                          pm02_nowcast)
                        self.database_manager.updateValue(record['dateTime'], f'airquality_{sensor}_pm10_nowcast',
                                                          pm10_nowcast)
                    except Exception as e:
                        log.error(f'AirGradient Ingest: Error calculating AQI for sensor {sensor}. {e}.')

    def calculate_aqi(self, serial_number, timestamp):
        """
        Calculates the 24-hour AQI from PM2.5 and PM10.
        """
        # Get time of record and time 24 hours before the record
        start_ts = timestamp - 86400
        stop_ts = timestamp

        # Create database query
        pm02_field_name = f'airquality_{serial_number}_pm02'
        pm10_field_name = f'airquality_{serial_number}_pm02'
        query = f'SELECT AVG({pm02_field_name}), AVG({pm10_field_name}) FROM {self.database_manager.table_name} WHERE dateTime>? AND dateTime<=?'

        # Get the mean PM2.5 and PM10 over the last 24 hours
        mean24hr_pm02, mean24hr_pm10 = self.database_manager.getSql(query, (start_ts, stop_ts))
        log.debug(f'AirGradient Ingest: {serial_number} 24-hr mean PM2.5 = {mean24hr_pm02}.')
        log.debug(f'AirGradient Ingest: {serial_number} 24-hr mean PM10 = {mean24hr_pm10}.')

        # Convert PM to AQI
        pm02_aqi = (round(pm02_to_aqi(mean24hr_pm02)) if mean24hr_pm02 is not None else None)
        pm10_aqi = (round(pm10_to_aqi(mean24hr_pm10)) if mean24hr_pm10 is not None else None)

        log.debug(f'AirGradient Ingest: {serial_number} PM2.5 AQI = {pm02_aqi}.')
        log.debug(f'AirGradient Ingest: {serial_number} PM10 AQI = {pm10_aqi}.')

        return pm02_aqi, pm10_aqi

    def calculate_nowcast_aqi(self, serial_number, timestamp):
        """
        Calculates the NowCast AQI for PM2.5 and PM10.
        """
        # Get hourly means over the last 12 hours for PM2.5 and PM10
        pm02_hourly_data, pm10_hourly_data = [], []
        for t in range(12):
            # Get one hour time range
            start_ts = timestamp - 3600 * t - 3600
            stop_ts = timestamp - 3600 * t

            # Create database query
            pm02_field_name = f'airquality_{serial_number}_pm02'
            pm10_field_name = f'airquality_{serial_number}_pm02'
            query = f'SELECT AVG({pm02_field_name}), AVG({pm10_field_name}) FROM {self.database_manager.table_name} WHERE dateTime>? AND dateTime<=?'

            # Get average PM2.5 and PM10 over time range
            hourly_avg = self.database_manager.getSql(query, (start_ts, stop_ts))
            pm02_hourly_data.append(hourly_avg[0])
            pm10_hourly_data.append(hourly_avg[1])

        # Calculate NowCast AQI from hourly PM data
        if len(pm02_hourly_data) >= 3:
            nowcast_pm02 = calculate_nowcast(pm02_hourly_data)
            pm02_nowcast_aqi = (pm02_to_aqi(nowcast_pm02) if nowcast_pm02 is not None else None)
        else:
            pm02_nowcast_aqi = None
        if len(pm10_hourly_data) >= 3:
            nowcast_pm10 = calculate_nowcast(pm10_hourly_data)
            pm10_nowcast_aqi = (pm10_to_aqi(nowcast_pm10) if nowcast_pm10 is not None else None)
        else:
            pm10_nowcast_aqi = None

        log.debug(f'AirGradient Ingest: {serial_number} PM2.5 NowCast AQI = {pm02_nowcast_aqi}.')
        log.debug(f'AirGradient Ingest: {serial_number} PM10 NowCast AQI = {pm10_nowcast_aqi}.')

        return pm02_nowcast_aqi, pm10_nowcast_aqi


class AirGradientDataThread(threading.Thread):

    def __init__(self, config_dict):
        threading.Thread.__init__(self, name='AirGradientDataIngest')
        user_config = config_dict.get('AirGradient', {})
        self.max_age_seconds = int(user_config['max_age_seconds'])
        self.sensors = user_config['sensors']
        self.polling_interval = int(user_config['polling_interval'])

        # Get unit system in use
        unit_system = config_dict['StdConvert']['target_unit']  # Options are 'US', 'METRICWX', or 'METRIC'
        if unit_system == 'US':
            self.units_temp = weewx.units.USUnits['group_temperature']
        elif unit_system == 'METRIC':
            self.units_temp = weewx.units.MetricUnits['group_temperature']
        elif unit_system == 'METRICWX':
            self.units_temp = weewx.units.MetricWXUnits['group_temperature']

        self._lock = threading.Lock()
        self._record = None
        self.running = False

    def get_record(self):
        with self._lock:
            if not self._record:
                return None
            else:
                return self._record.copy()

    def run(self):
        self.running = True

        while self.running:
            try:
                record = self.new_archive_record()
                with self._lock:
                    self._record = record
                time.sleep(self.polling_interval)
            except Exception as e:
                log.error(f'AirGradient Ingest: Error generating record. {e}.')

    def new_archive_record(self):
        """
        Creates a new archive record of data from each AirGradient sensor.
        """
        record = dict()
        record['dateTime'] = int(time.time())
        record['usUnits'] = weewx.US
        record['interval'] = self.polling_interval

        # Get data from each sensor
        for sensor in self.sensors:

            # Get data from sensor
            data = get_sensor_data(sensor)

            # Create record
            if data is not None:
                log.info(f"AirGradient Ingest: Getting data from sensor {sensor}.")

                # Get data from sensor
                record[f'airquality_{sensor}_pm01'] = get_value(data, 'pm01', 0)
                record[f'airquality_{sensor}_pm02'] = get_value(data, 'pm02', 0)
                record[f'airquality_{sensor}_pm10'] = get_value(data, 'pm10', 0)
                record[f'airquality_{sensor}_pm003_count'] = get_value(data, 'pm003Count', 0)
                record[f'airquality_{sensor}_rhum'] = get_value(data, 'rhum', 0, 100)
                record[f'airquality_{sensor}_rhum_compensated'] = get_value(data, 'rhumCompensated', 0, 100)
                record[f'airquality_{sensor}_rco2'] = get_value(data, 'rco2', 0)
                record[f'airquality_{sensor}_tvoc_raw'] = get_value(data, 'tvocRaw', 0)
                record[f'airquality_{sensor}_tvoc_index'] = get_value(data, 'tvocIndex', 0)
                record[f'airquality_{sensor}_nox_raw'] = get_value(data, 'noxRaw', 0)
                record[f'airquality_{sensor}_nox_index'] = get_value(data, 'noxIndex', 0)
                record[f'airquality_{sensor}_wifi'] = get_value(data, 'wifi')

                # Get temperature in correct units
                atmp = get_value(data, 'atmp', -100, 100)
                atmp_compensated = get_value(data, 'atmpCompensated', -100, 100)
                if atmp is not None and self.units_temp != 'degree_C':
                    conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                    record[f'airquality_{sensor}_atmp'] = conversion(atmp)
                    record[f'airquality_{sensor}_atmp_compensated'] = conversion(atmp_compensated)
                else:
                    record[f'airquality_{sensor}_atmp'] = atmp
                    record[f'airquality_{sensor}_atmp_compensated'] = atmp_compensated

            else:
                log.warning(f"AirGradient Ingest: No data found from sensor {sensor}.")

        return record
