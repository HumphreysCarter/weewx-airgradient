#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""User extensions module

This module is imported from the main executable, so anything put here will be
executed before anything else happens. This makes it a good place to put user
extensions.
"""

import locale
# This will use the locale specified by the environment variable 'LANG'
# Other options are possible. See:
# http://docs.python.org/2/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')

# Set units for AirGradient sensors
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
