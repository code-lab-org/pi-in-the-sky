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
pub_frequency = int(pub_frequency)
print("Enter simulation timestep (s): ")
delta_time_sim = input() # Seconds the simulation advances every loop
delta_time_sim = int(delta_time_sim)
undetected_fires = []
avg_det_time = 0

new_fires = get_fires('random')
num_of_fires = len(new_fires)

active_fires_json = {"type": "Feature", \
                "geometry": {
                    "type": "MultiPoint",
                    "coordinates": []}
                }
detected_fires_json = {"type": "Feature", \
"geometry": {
    "type": "MultiPoint",
    "coordinates": []}
}

curr_time = datetime.now().replace(microsecond=0, tzinfo=utc)
curr_time = datetime(2020, 1, 1, 7, 0, tzinfo=utc)
pub_time = datetime.now().replace(microsecond=0) + timedelta(seconds=pub_frequency)
start = datetime.now()

while True:
    loop_begin = datetime.now()

    sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time)))

    for fire in new_fires:
        if fire.det_time < curr_time:
            active_fires_json['geometry']['coordinates'].append([float(fire.pos.latitude.degrees), float(fire.pos.longitude.degrees)])
            undetected_fires.append(fire)
            new_fires.remove(fire)

    for fire in undetected_fires:
        if detect(sat_pos.at(ts.from_datetime(curr_time)), fire.pos.at(ts.from_datetime(curr_time))):
            detected_fires_json['geometry']['coordinates'].append([float(fire.pos.latitude.degrees), float(fire.pos.longitude.degrees)])
            undetected_fires.remove(fire)
        # if fire.det_time > curr_time or fire in detected_fires:
        #     continue
        # elif fire.det_time <= curr_time and fire not in active_fires:
        #     active_fires.append(fire)
        # elif detect(sat_pos.at(ts.from_datetime(curr_time)), fire.pos.at(ts.from_datetime(curr_time))) and fire not in detected_fires:
        #     detected_fires.append(fire)
        #     avg_det_time += (curr_time - fire.det_time).total_seconds()

    loop_end = datetime.now()

    if pub_frequency >= (loop_end - loop_begin).total_seconds():
            time.sleep(pub_frequency - (loop_end - loop_begin).total_seconds())


    print(f"publishing: {curr_time} \n {sat_pos} \n {str(active_fires_json)} \n {str(detected_fires_json)}")
    client.publish("time", curr_time.isoformat())
    client.publish("position", str(sat_pos))
    client.publish("active_fires", str(active_fires_json))
    client.publish("detected_fires", str(detected_fires_json))


    curr_time += timedelta(seconds=delta_time_sim)
    pub_time += timedelta(seconds=pub_frequency)

    if len(detected_fires_json['geometry']['coordinates']) == num_of_fires:
        end = datetime.now()
        print(f"Speed: {(end - start).total_seconds()}")

        time.sleep(2)   
        break

client.loop_stop()
