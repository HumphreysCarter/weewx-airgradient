import sqlite3
from datetime import datetime


def calculate_nowcast(pm_measurements):
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


# Connect to the SQLite database
conn = sqlite3.connect('/home/pi/weewx/archive/weewx.sdb')
cursor = conn.cursor()

# Retrieve PM measurements from the database
cursor.execute("SELECT dateTime, ag_out_pm02 FROM archive WHERE ag_out_pm02 IS NOT NULL")
rows = cursor.fetchall()

# List to store tuples of (timestamp, PM2.5 NowCast AQI, PM10 NowCast AQI)
update_values = []

# Iterate over each row in the database
for row in rows:
    timestamp, pm_measurement = row
    print(f'Calculating NowCast AQI for {datetime.fromtimestamp(timestamp)} ({timestamp})')

    # Get hourly means over the last 12 hours for PM2.5 and PM10
    pm02_hourly_data, pm10_hourly_data = [], []
    for t in range(12):
        start_ts = timestamp - 3600 * t - 3600
        stop_ts = timestamp - 3600 * t

        cursor.execute("SELECT AVG(ag_out_pm02), AVG(ag_out_pm10) FROM archive WHERE dateTime>? AND dateTime<=?",
                       (start_ts, stop_ts))
        hourly_avg = cursor.fetchall()
        if hourly_avg[0][0] is not None:
            pm02_hourly_data.append(hourly_avg[0][0])
        if hourly_avg[0][1] is not None:
            pm10_hourly_data.append(hourly_avg[0][1])

    # Calculate NowCast AQI from hourly data PM data
    if len(pm02_hourly_data) >= 3:
        pm02_nowcast_aqi = pm02_to_aqi(calculate_nowcast(pm02_hourly_data))
    else:
        pm02_nowcast_aqi = None
    if len(pm10_hourly_data) >= 3:
        pm10_nowcast_aqi = pm10_to_aqi(calculate_nowcast(pm10_hourly_data))
    else:
        pm10_nowcast_aqi = None
    print(f'\tPM2.5 NowCast AQI = {pm02_nowcast_aqi}')
    print(f'\tPM10 NowCast AQI = {pm10_nowcast_aqi}')

    # Add to list if NowCast calculation was successful
    if pm02_nowcast_aqi is not None and pm10_nowcast_aqi is not None:
        update_values.append((pm02_nowcast_aqi, pm10_nowcast_aqi, timestamp))

# Update database
print('Updating database...')
cursor.executemany("UPDATE archive SET ag_out_pm02_nowcast = ?, ag_out_pm10_nowcast = ? WHERE dateTime = ?",
                   update_values)

# Commit changes and close connection
conn.commit()
conn.close()

