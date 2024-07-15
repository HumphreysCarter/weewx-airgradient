import sys
import json
import weewx
import weewx.units
import urllib.request
from weewx.engine import StdService
from datetime import datetime

import logging
log = logging.getLogger(__name__)

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 9):
    raise weewx.UnsupportedFeature(
        " weewx-airgradient requires Python 3.9 or later, found %s.%s" % (sys.version_info[0], sys.version_info[1]))

if weewx.__version__ < "4":
    raise weewx.UnsupportedFeature(
        " weewx-airgradient requires WeeWX 4, found %s" % weewx.__version__)

# Set units for AirGradient variables
weewx.units.obs_group_dict["ag_out_pm02_aqi"] = "group_count"
weewx.units.obs_group_dict["ag_out_pm10_aqi"] = "group_count"
weewx.units.obs_group_dict["ag_out_pm02_nowcast"] = "group_count"
weewx.units.obs_group_dict["ag_out_pm10_nowcast"] = "group_count"
weewx.units.obs_group_dict["ag_out_pm01"] = "group_concentration"
weewx.units.obs_group_dict["ag_out_pm02"] = "group_concentration"
weewx.units.obs_group_dict["ag_out_pm10"] = "group_concentration"
weewx.units.obs_group_dict["ag_out_atmp"] = "group_temperature"
weewx.units.obs_group_dict["ag_out_rhum"] = "group_percent"
weewx.units.obs_group_dict["ag_out_rco2"] = "group_fraction"
weewx.units.obs_group_dict["ag_out_tvoc"] = "group_concentration"
weewx.units.obs_group_dict["ag_out_tvoc_index"] = "group_count"
weewx.units.obs_group_dict["ag_out_nox"] = "group_concentration"
weewx.units.obs_group_dict["ag_out_nox_index"] = "group_count"
weewx.units.obs_group_dict["ag_in_rco2"] = "group_fraction"
weewx.units.obs_group_dict["ag_in_pm01"] = "group_concentration"
weewx.units.obs_group_dict["ag_in_pm02"] = "group_concentration"
weewx.units.obs_group_dict["ag_in_pm10"] = "group_concentration"
weewx.units.obs_group_dict["ag_in_tvoc"] = "group_concentration"
weewx.units.obs_group_dict["ag_in_tvoc_index"] = "group_count"
weewx.units.obs_group_dict["ag_in_nox"] = "group_concentration"
weewx.units.obs_group_dict["ag_in_nox_index"] = "group_count"
weewx.units.obs_group_dict["ag_in_atmp"] = "group_temperature"
weewx.units.obs_group_dict["ag_in_rhum"] = "group_percent"

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


def get_sensor_data(sensor_ip):
    try:
        with urllib.request.urlopen(f'http://{sensor_ip}/measures/current') as url:
            return json.load(url)

    except urllib.error.URLError as e:
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


class IngestAirGradientData(StdService):

    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(IngestAirGradientData, self).__init__(engine, config_dict)

        # Bind to any new archive record events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        # Get unit system in use
        unit_system = config_dict['StdConvert']['target_unit']  # Options are 'US', 'METRICWX', or 'METRIC'
        if unit_system == 'US':
            self.units_temp = weewx.units.USUnits['group_temperature']
        elif unit_system == 'METRIC':
            self.units_temp = weewx.units.MetricUnits['group_temperature']
        elif unit_system == 'METRICWX':
            self.units_temp = weewx.units.MetricWXUnits['group_temperature']

        # Get data from config
        self.outdoor_sensor = '10.101.107.101'
        self.indoor_sensor = '10.101.107.102'
        self.max_age_seconds = 120

    def calculate_aqi(self, event):
        """
        Calculates the 24-hour AQI from PM2.5 and PM10.
        """
        # Start weewx database access
        db_manager = self.engine.db_binder.get_manager(data_binding='wx_binding', initialize=True)

        # Get time of record and time 24 hours before the record
        start_ts = event.record['dateTime'] - 86400
        stop_ts = event.record['dateTime']

        # Get the mean PM2.5 and PM10 over the last 24 hours
        mean24hr_pm02, mean24hr_pm10 = db_manager.getSql(
            "SELECT AVG(ag_out_pm02), AVG(ag_out_pm10) FROM %s WHERE dateTime>? AND dateTime<=?" % db_manager.table_name,
            (start_ts, stop_ts))
        log.debug(f"AirGradient Ingest: 24-hr mean PM2.5 = {mean24hr_pm02}.")
        log.debug(f"AirGradient Ingest: 24-hr mean PM10 = {mean24hr_pm10}.")

        # Convert PM to AQI
        pm02_aqi = round(pm02_to_aqi(mean24hr_pm02))
        pm10_aqi = round(pm10_to_aqi(mean24hr_pm02))

        log.debug(f"AirGradient Ingest: PM2.5 AQI = {pm02_aqi}.")
        log.debug(f"AirGradient Ingest: PM10 AQI = {pm10_aqi}.")

        event.record['ag_out_pm02_aqi'] = pm02_aqi
        event.record['ag_out_pm10_aqi'] = pm10_aqi

    def calculate_nowcast_aqi(self, event):
        """
        Calculates the NowCast AQI for PM2.5 and PM10.
        """
        # Start weewx database access
        db_manager = self.engine.db_binder.get_manager(data_binding='wx_binding', initialize=True)

        # Get hourly means over the last 12 hours for PM2.5 and PM10
        pm02_hourly_data, pm10_hourly_data = [], []
        for t in range(12):
            start_ts = event.record['dateTime'] - 3600 * t - 3600
            stop_ts = event.record['dateTime'] - 3600 * t

            hourly_avg = db_manager.getSql(
                "SELECT AVG(ag_out_pm02), AVG(ag_out_pm10) FROM %s WHERE dateTime>? AND dateTime<=?" % db_manager.table_name,
                (start_ts, stop_ts))
            pm02_hourly_data.append(hourly_avg[0])
            pm10_hourly_data.append(hourly_avg[1])

        # Calculate NowCast AQI from hourly data PM data
        if len(pm02_hourly_data) >= 3:
            pm02_nowcast_aqi = pm02_to_aqi(calculate_nowcast(pm02_hourly_data))
        else:
            pm02_nowcast_aqi = None
        if len(pm10_hourly_data) >= 3:
            pm10_nowcast_aqi = pm10_to_aqi(calculate_nowcast(pm10_hourly_data))
        else:
            pm10_nowcast_aqi = None

        log.debug(f"AirGradient Ingest: PM2.5 NowCast AQI = {pm02_nowcast_aqi}.")
        log.debug(f"AirGradient Ingest: PM10 NowCast AQI = {pm10_nowcast_aqi}.")

        event.record['ag_out_pm02_nowcast'] = pm02_nowcast_aqi
        event.record['ag_out_pm10_nowcast'] = pm10_nowcast_aqi

    def new_archive_record(self, event):
        # Get datetime of weewx record
        record_dt = datetime.utcfromtimestamp(event.record['dateTime'])
        log.debug(f"AirGradient Ingest: {record_dt}")

        # Check if time delta close enough to record. Keeps current data from getting assigned to old data.
        delta = (datetime.utcnow() - record_dt).total_seconds()
        if delta > self.max_age_seconds:
            log.debug(
                f"AirGradient Ingest: Skipping record {datetime.fromtimestamp(event.record['dateTime'])} ({event.record['dateTime']}). Record old.")
        else:
            # Get data from outdoor sensor
            if self.outdoor_sensor is not None:

                data = get_sensor_data(self.outdoor_sensor)

                if data is not None:
                    log.debug(f"AirGradient Ingest: Getting data from sensor {get_value(data, 'serialno')}")

                    # Get sensor data
                    event.record['ag_out_pm01'] = get_value(data, 'pm01', 0)
                    event.record['ag_out_pm02'] = get_value(data, 'pm02', 0)
                    event.record['ag_out_pm10'] = get_value(data, 'pm10', 0)
                    atmp = get_value(data, 'atmp', -100, 100)
                    if atmp is not None and self.units_temp != 'degree_C':
                        conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                        event.record['ag_out_atmp'] = conversion(atmp)
                    else:
                        event.record['ag_out_atmp'] = atmp
                    event.record['ag_out_rhum'] = get_value(data, 'rhum', 0, 100)
                    event.record['ag_out_wifi'] = get_value(data, 'wifi')
                    event.record['ag_out_tvoc_index'] = get_value(data, 'tvocIndex', 0)
                    event.record['ag_out_tvoc'] = get_value(data, 'tvocRaw', 0)
                    event.record['ag_out_nox_index'] = get_value(data, 'noxIndex', 0)
                    event.record['ag_out_nox'] = get_value(data, 'noxRaw', 0)
                    event.record['ag_out_rco2'] = get_value(data, 'rco2', 0)

                    # Calculate AQI
                    self.calculate_aqi(event)

                    # Calculate NowCast AQI
                    self.calculate_nowcast_aqi(event)
                else:
                    log.debug(f"AirGradient Ingest: No data found from sensor at {self.outdoor_sensor}")

            # Get data from indoor sensor
            if self.indoor_sensor is not None:
                data = get_sensor_data(self.indoor_sensor)

                if data is not None:
                    log.debug(f"AirGradient Ingest: Getting data from sensor {get_value(data, 'serialno')}")

                    event.record['ag_in_rco2'] = get_value(data, 'rco2', 0)
                    event.record['ag_in_pm01'] = get_value(data, 'pm01', 0)
                    event.record['ag_in_pm02'] = get_value(data, 'pm02', 0)
                    event.record['ag_in_pm10'] = get_value(data, 'pm10', 0)
                    event.record['ag_in_tvoc_index'] = get_value(data, 'tvocIndex', 0)
                    event.record['ag_in_tvoc'] = get_value(data, 'tvocRaw', 0)
                    event.record['ag_in_nox_index'] = get_value(data, 'noxIndex', 0)
                    event.record['ag_in_nox'] = get_value(data, 'noxRaw', 0)

                    atmp = get_value(data, 'atmp', -100, 100)
                    if atmp is not None and self.units_temp != 'degree_C':
                        conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                        event.record['ag_in_atmp'] = conversion(atmp)
                    else:
                        event.record['ag_in_atmp'] = atmp
                    event.record['ag_in_rhum'] = get_value(data, 'rhum', 0, 100)
                    event.record['ag_in_wifi'] = get_value(data, 'wifi')

                else:
                    log.debug(f"AirGradient Ingest: No data from sensor at {self.indoor_sensor}")
