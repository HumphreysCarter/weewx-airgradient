import json
import weewx
import weewx.units
from weewx.engine import StdService
from datetime import datetime

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
        self.api_directory = '/home/pi/air-quality/data/api/'
        self.stale_minutes = 5
        self.outdoor_sensor = '84fce60c06c4'
        self.indoor_sensor = '84fce60e9b6c'

    def get_sensor_data(self, serial_number):
        with open(f'{self.api_directory}/AirGradient_{serial_number}.json', 'r') as f:
            data = json.load(f)

        # Only return data if data no more than 1 minute old
        data_date = datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M:%S.%f')
        if (datetime.utcnow()-data_date).total_seconds() <= self.stale_minutes * 60:
            return data

        return None

    def correct_rhum(self, raw_rhum):
        """
        Corrects relative humidity reading based on AirGradient provided correction
        details: https://forum.airgradient.com/t/open-air-outdoor-air-quality-monitor-humidity-readings-are-off/1171/2
        """
        return raw_rhum * 1.3921 - 1.0245
    def correct_atmp(self, raw_atmp):
        """
        Corrects air temperature reading based on AirGradient provided correction
        details: https://forum.airgradient.com/t/outdoor-temperature-and-humidity-reading-correction/1544/19
        """
        if raw_atmp < 10.0:
            return raw_atmp * 1.327 - 6.738
        else:
            return raw_atmp * 1.181 - 5.113

    def get_value(self, data, key):
        try:
            return data[key]
        except KeyError as e:
            return None

    def new_archive_record(self, event):
        # Get data from outdoor sensor
        if self.outdoor_sensor is not None:
            data = self.get_sensor_data(self.outdoor_sensor)

            if data is not None:
                event.record['ag_out_pm01'] = self.get_value(data, 'pm01')
                event.record['ag_out_pm02'] = self.get_value(data, 'pm02')
                event.record['ag_out_pm10'] = self.get_value(data, 'pm10')
                atmp = self.correct_atmp(self.get_value(data, 'atmp'))
                if self.units_temp != 'degree_C':
                    conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                    event.record['ag_out_atmp'] = conversion(atmp)
                else:
                    event.record['ag_out_atmp'] = atmp
                event.record['ag_out_rhum'] = self.correct_rhum(self.get_value(data, 'rhum'))
                event.record['ag_out_wifi'] = self.get_value(data, 'wifi')
                event.record['ag_out_tvoc'] = self.get_value(data, 'tvoc_index')
                event.record['ag_out_nox'] = self.get_value(data, 'nox_index')
                event.record['ag_out_rco2'] = self.get_value(data, 'rco2')


        # Get data from indoor sensor
        if self.indoor_sensor is not None:
            data = self.get_sensor_data(self.indoor_sensor)

            if data is not None:
                event.record['ag_in_rco2'] = self.get_value(data, 'rco2')
                event.record['ag_in_pm01'] = self.get_value(data, 'pm01')
                event.record['ag_in_pm02'] = self.get_value(data, 'pm02')
                event.record['ag_in_pm10'] = self.get_value(data, 'pm10')
                event.record['ag_in_tvoc'] = self.get_value(data, 'tvoc_index')
                event.record['ag_in_nox'] = self.get_value(data, 'nox_index')
                atmp = self.get_value(data, 'atmp')
                if self.units_temp != 'degree_C':
                    conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                    event.record['ag_in_atmp'] = conversion(atmp)
                else:
                    event.record['ag_in_atmp'] = atmp
                event.record['ag_in_rhum'] = self.get_value(data, 'rhum')
                event.record['ag_in_wifi'] = self.get_value(data, 'wifi')