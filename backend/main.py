from datetime import datetime, timedelta
from types import new_class
from venv import create
import numpy as np
from pytz import timezone
import time

import paho.mqtt.client as mqtt
from skyfield.api import load, wgs84, utc
from skyfield.framelib import itrs

from fires.fire import get_fires, create_geojson
from detect import detect

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


ts = load.timescale()
stations_url = 'http://celestrak.com/NORAD/elements/noaa.txt'
satellites = load.tle_file(stations_url, reload=True)
by_name = {sat.name: sat for sat in satellites}
satellite = by_name['SUOMI NPP [+]']
epoch = satellite.epoch
eastern = timezone('US/Eastern')
print(f'The most recent epoch is: \nUTC: {epoch.utc_datetime()} \n ET: {epoch.astimezone(eastern)}')

client = mqtt.Client()
client.on_connect = on_connect

client.connect("pi-in-the-sky.code-lab.org", 1883)

client.loop_start()

print("Enter publish frequency (s): ")
pub_frequency = input() # How often the sim should loop in seconds
pub_frequency = float(pub_frequency)
print("Enter simulation timestep (s): ")
delta_time_sim = input() # Seconds the simulation advances every loop
delta_time_sim = float(delta_time_sim)

active_fires = []
undetected_fires = []
detected_fires = []

# Get dataset of Fire objects
future_fires = get_fires('random')
num_of_fires = len(future_fires)

# Empty GeoJSON point
geojson = {"type": "point", \
                "coordinates": []}

curr_time = datetime(2020, 1, 1, 7, 0, tzinfo=utc)
pub_time = datetime.now().replace(microsecond=0) + timedelta(seconds=pub_frequency)
start = datetime.now()


# Simulation loop
while True:
    loop_begin = datetime.now()

    # Get satellite position and convert it to GeoJSON
    sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time)))
    geo_pos = geojson.copy()
    geo_pos["coordinates"] = [sat_pos.longitude.degrees, sat_pos.latitude.degrees, sat_pos.elevation.m]

    # Loop through fires that haven't started
    new_undetected_fires = []
    for fire in future_fires:
        # Check if fire should start this loop
        if fire.det_time < curr_time and fire not in active_fires:
            # Create GeoJSON point object of fire
            geo_fire = geojson.copy()
            geo_fire["coordinates"] = [fire.pos.longitude.degrees, fire.pos.latitude.degrees]
            # Adds GeoJSON to list of newly started fires
            new_undetected_fires.append(geo_fire)
            # Adds Fire object to list of active undetected fires
            undetected_fires.append(fire)
            # Adds Fire object to list of all active fires
            active_fires.append(fire)
            # Removes new fire from list of yet unstarted fires
            future_fires.remove(fire)

    # Loop through active fires that haven't been detected yet
    new_detected_fires = []
    for fire in undetected_fires:
        # Check if satellite detects fire
        if detect(sat_pos.at(ts.from_datetime(curr_time)), fire.pos.at(ts.from_datetime(curr_time))):
            # Create GeoJSON point object of fire
            geo_fire = geojson.copy()
            geo_fire["coordinates"] = [fire.pos.longitude.degrees, fire.pos.latitude.degrees]
            # Adds GeoJSON to list of newly detected fires
            new_detected_fires.append(geo_fire)
            # Adds Fire object to list of all detected fires
            detected_fires.append(fire)
            # Removes newly detected Fire object from list of all undetected fires
            undetected_fires.remove(fire)

    loop_end = datetime.now()

    # Sleep for the remaining time until the next publish time
    if pub_frequency >= (loop_end - loop_begin).total_seconds():
            time.sleep(pub_frequency - (loop_end - loop_begin).total_seconds())

    # Print and publish the current time
    print(f"time: {curr_time.isoformat()}")
    client.publish("time", curr_time.isoformat())

    # Print and publish the satellite position
    print(f"position: {str(geo_pos)}")
    client.publish("position", str(geo_pos))

    # Loop through the new active fires and print and publish them individually
    for geo_fire in new_undetected_fires:
        print(f"active: {str(geo_fire)}")
        client.publish("active_fires", str(geo_fire))

    # Loop through the new detected fires and print and publish them individually
    for geo_fire in new_detected_fires:
        print(f"detected: {str(geo_fire)}")
        client.publish("detected_fires", str(geo_fire))

    # Increment simulation time and publish time
    curr_time += timedelta(seconds=delta_time_sim)
    pub_time += timedelta(seconds=pub_frequency)

    # Checks if all fires have been detected and end the sim if they have
    if len(detected_fires) == num_of_fires:
        end = datetime.now()
        print(f"Speed: {(end - start).total_seconds()}")
        time.sleep(2)   
        break

client.loop_stop()
