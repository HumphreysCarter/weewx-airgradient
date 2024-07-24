> [!WARNING]
> This extension is still a work in progress. Use at your own risk.

# WeeWx AirGradient Extension
A [WeeWx](https://weewx.com/) extension for ingesting data from AirGradient indoor and outdoor air quality monitors.

![](weewx-example.png)

## Requirements

* Python 3.9 or later
* WeeWx version 5

## Installation

This extension can be installed with `weectl extension` using the commands below.

```
$ source ~/weewx-venv/bin/activate
$ weectl extension install https://github.com/HumphreysCarter/weewx-airgradient/releases/latest/download/weewx-airgradient.zip
```

The installation script will prompt you to enter the serial number for each airgradient sensor on your network. Serial numbers should be entered one at a time, pressing enter at the end of each to move to the next prompt. Once all have been entered, type `done` into the prompt to finish the installation.