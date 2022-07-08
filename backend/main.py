from datetime import datetime, timedelta
import numpy as np
from pytz import timezone
import time

import paho.mqtt.client as mqtt
from skyfield.api import load, wgs84, utc
from skyfield.framelib import itrs

from fires.fire import get_fires
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

client.connect("localhost", 1883)

client.loop_start()

start_time = datetime(2020, 1, 1, 7, 0, tzinfo=utc)
pub_frequency = 0.1 # How often the sim should loop in seconds
delta_time_sim = 60 # Seconds the simulation advances every loop
active_fires = []
detected_fires = []
avg_det_time = 0

all_fires = get_fires('random')

curr_time = start_time
pub_time = datetime.now().replace(microsecond=0) + timedelta(seconds=pub_frequency)
start = datetime.now()

while True:
    loop_begin = datetime.now()

    sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time)))

    for fire in all_fires:
        if fire.det_time > curr_time or fire in detected_fires:
            continue
        if fire.det_time <= curr_time and fire not in active_fires:
            active_fires.append(fire)
        if detect(sat_pos.at(ts.from_datetime(curr_time)), fire.pos.at(ts.from_datetime(curr_time))) and fire not in detected_fires:
            detected_fires.append(fire)
            avg_det_time += (curr_time - fire.det_time).total_seconds()

    print(f"publishing: {curr_time} \n {sat_pos} \n {[len(active_fires), len(detected_fires)]}")
    client.publish("time", curr_time.isoformat())
    client.publish("position", str(sat_pos))
    client.publish("active_fires", str([len(active_fires), len(detected_fires)]))

    loop_end = datetime.now()

    if pub_frequency >= (loop_end - loop_begin).total_seconds():
        time.sleep(pub_frequency - (loop_end - loop_begin).total_seconds())

    curr_time += timedelta(seconds=delta_time_sim)
    pub_time += timedelta(seconds=pub_frequency)

    if len(detected_fires) == len(all_fires):
        end = datetime.now()
        print("All fires detected.")
        print(f"The average time to detect a fire was {avg_det_time / (60 * len(detected_fires))} minutes. The simulation took {(end - start).total_seconds()} seconds to run with a {delta_time_sim} second timestep.")
        client.publish("position", f"The average time to detect a fire was {avg_det_time / (60 * len(detected_fires))} minutes. The simulation took {(end - start).total_seconds()} seconds to run with a {delta_time} second timestep.")

        time.sleep(1)
        break
