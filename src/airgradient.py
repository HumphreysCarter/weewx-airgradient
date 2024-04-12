import json
import weewx
import weewx.units
import urllib.request
from weewx.engine import StdService
from datetime import datetime


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
    with urllib.request.urlopen(f'http://{sensor_ip}/measures/current') as url:
        data = json.load(url)

    # Only return data if data no more than 1 minute old
    # data_date = datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M:%S.%f')
    # if (datetime.utcnow()-data_date).total_seconds() <= self.stale_minutes * 60:
    #    return data

    return data


class AddAirGradientData(StdService):

    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(AddAirGradientData, self).__init__(engine, config_dict)

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

    def new_archive_record(self, event):
        # Get data from outdoor sensor
        if self.outdoor_sensor is not None:
            data = get_sensor_data(self.outdoor_sensor)

            if data is not None:
                event.record['ag_out_pm01'] = get_value(data, 'pm01')
                event.record['ag_out_pm02'] = get_value(data, 'pm02')
                event.record['ag_out_pm10'] = get_value(data, 'pm10')
                atmp = get_value(data, 'atmp', -100, 100)
                if self.units_temp != 'degree_C':
                    conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                    event.record['ag_out_atmp'] = conversion(atmp)
                else:
                    event.record['ag_out_atmp'] = atmp
                event.record['ag_out_rhum'] = get_value(data, 'rhum', 0, 100)
                event.record['ag_out_wifi'] = get_value(data, 'wifi')
                event.record['ag_out_tvoc_index'] = get_value(data, 'tvocIndex')
                event.record['ag_out_tvoc'] = get_value(data, 'tvoc_raw')
                event.record['ag_out_nox_index'] = get_value(data, 'noxIndex')
                event.record['ag_out_nox'] = get_value(data, 'nox_raw')
                event.record['ag_out_rco2'] = get_value(data, 'rco2')

        # Get data from indoor sensor
        if self.indoor_sensor is not None:
            data = get_sensor_data(self.indoor_sensor)

            if data is not None:
                event.record['ag_in_rco2'] = get_value(data, 'rco2')
                event.record['ag_in_pm01'] = get_value(data, 'pm01')
                event.record['ag_in_pm02'] = get_value(data, 'pm02')
                event.record['ag_in_pm10'] = get_value(data, 'pm10')
                event.record['ag_in_tvoc_index'] = get_value(data, 'tvocIndex')
                event.record['ag_in_tvoc'] = get_value(data, 'tvoc_raw')
                event.record['ag_in_nox_index'] = get_value(data, 'noxIndex')
                event.record['ag_in_nox'] = get_value(data, 'nox_raw')

                atmp = get_value(data, 'atmp', -100, 100)
                if self.units_temp != 'degree_C':
                    conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                    event.record['ag_in_atmp'] = conversion(atmp)
                else:
                    event.record['ag_in_atmp'] = atmp
                event.record['ag_in_rhum'] = get_value(data, 'rhum', 0, 100)
                event.record['ag_in_wifi'] = get_value(data, 'wifi')
