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
sim_time = 0
delta_time = 60
old_fires = ''
active_fires = []
detected_fires = []
avg_det_time = 0
all_fires = get_fires('random')

while True:
    now = datetime.now().isoformat()
    curr_time = start_time + timedelta(seconds=sim_time)

    sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time)))

    new_fires = ''
    for fire in all_fires:
        if fire.det_time > curr_time or str(fire.pos) in detected_fires:
            continue
        if fire.det_time <= curr_time and fire not in active_fires:
            active_fires.append(fire)
        if detect(sat_pos.at(ts.from_datetime(curr_time)), fire.pos.at(ts.from_datetime(curr_time))) and fire not in detected_fires:
            detected_fires.append(str(fire.pos))
            avg_det_time += (curr_time - fire.det_time).total_seconds()
            new_fires += (str(fire.pos) + '\n')


    print(f"publishing: {curr_time} \n {sat_pos} \n {new_fires} \n {[len(active_fires), len(detected_fires)]}")
    client.publish("time", curr_time.isoformat())
    client.publish("position", str(sat_pos))
    client.publish("active_fires", str([len(active_fires), len(detected_fires)]))
    # time.sleep(0.5)
    sim_time += 30

    if len(detected_fires) == len(all_fires):
        print("All fires detected.")
        print(f"The average time to detect fire was {avg_det_time / (60 * len(detected_fires))} minutes.")
        client.publish("position", f"The average time to detect a fire was {avg_det_time / (60 * len(detected_fires))} minutes.")
        time.sleep(1)
        break
