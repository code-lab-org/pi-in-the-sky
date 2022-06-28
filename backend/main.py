from datetime import datetime
import numpy as np
from pytz import timezone
import time

import paho.mqtt.client as mqtt
from skyfield.api import load, wgs84
from skyfield.framelib import itrs


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

while True:
    now = datetime.now().isoformat()
    pos = wgs84.geographic_position_of(satellite.at(ts.now()))
    print(f"publishing: {now} \n {pos}")
    client.publish("time", now)
    client.publish("position", str(pos))
    time.sleep(1)