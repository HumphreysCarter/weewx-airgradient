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

from weecfg.extension import ExtensionInstaller


def loader():
    return AirGradientInstaller()


def get_serial_numbers():
    serial_numbers = []

    print('Enter a serial number for each AirGradient sensor. Press enter after each serial number or (or type '
          '\'done\' to finish)\nSerial numbers can be found under hardware on the AirGradient dashboard.')
    while True:
        serial_number = input("Sensor serial number: ")
        if serial_number.lower() == 'done':
            break
        serial_numbers.append(serial_number)
    return serial_numbers


class AirGradientInstaller(ExtensionInstaller):
    def __init__(self):
        # Get sensor serial numbers
        sensors = get_serial_numbers()

        # Create weewx config
        super(AirGradientInstaller, self).__init__(
            version='0.1',
            name='airgradient',
            description='Data ingest for AirGradient air quality monitors.',
            author='Carter Humphreys',
            author_email='carter.humphreys@lake-effect.dev',
            process_services='user.airgradient.AirGradientDataIngest',
            config={
                'StdReport': {
                    'AirGradient': {
                        'skin': 'AirGradient',
                        'enable': 'true',
                        'HTML_ROOT': 'airquality',
                        'extras': {
                            'sensors': sensors,
                        }
                    },
                },
                'AirGradient': {
                    'data_binding': 'airgradient_binding',
                    'polling_interval': 60,
                    'max_age_seconds': 120,
                    'sensors': sensors,
                },
                'DataBindings': {
                    'airgradient_binding': {
                        'database': 'airgradient_sqlite',
                        'table_name': 'archive',
                        'manager': 'weewx.manager.DaySummaryManager',
                        'schema': 'user.airgradient.schema'
                    }
                },
                'Databases': {
                    'airgradient_sqlite': {
                        'database_name': 'airgradient.sdb',
                        'driver': 'weedb.sqlite'
                    }
                },
            },
            files=[
                ('bin/user/', ['bin/user/airgradient.py']),
                ('skins/AirGradient', [
                    'skins/AirGradient/index.html.tmpl',
                    'skins/AirGradient/skin.conf',
                ]),
            ]
        )
