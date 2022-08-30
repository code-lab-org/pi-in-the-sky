from datetime import datetime, timedelta
from types import new_class
from venv import create
import numpy as np
from pytz import timezone
import time
import json
import sys

import paho.mqtt.client as mqtt
from skyfield.api import load, wgs84, utc
from skyfield.framelib import itrs

from fires.fire import get_fires, create_geojson
from detect import detect

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def main():
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

    pub_frequency = float(sys.argv[1])
    delta_time_sim = float(sys.argv[2])
    fire_dataset = str(sys.argv[3])

    active_fires = []
    undetected_fires = []
    detected_fires = []

    # Get dataset of Fire objects
    future_fires = get_fires(fire_dataset)
    num_of_fires = len(future_fires)

    # To determine calculation speed
    sim_start = datetime.now()
    curr_time = datetime.now(tz=utc)
    start_time = datetime.now(tz=utc)
    pub_time = datetime.now().replace(microsecond=0) + timedelta(seconds=pub_frequency)



    # Simulation loop
    while True:
        loop_begin = datetime.now()

        # Get satellite position and convert it to GeoJSON
        sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time)))
        next_sat_pos = wgs84.geographic_position_of(satellite.at(ts.from_datetime(curr_time + timedelta(seconds=delta_time_sim))))

        geo_pos = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [sat_pos.longitude.degrees, sat_pos.latitude.degrees, sat_pos.elevation.m]
            }
        }
        # geo_pos = {
        #     "type": "FeatureCollection",
        #     "features": [{
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [sat_pos.longitude.degrees, sat_pos.latitude.degrees, sat_pos.elevation.m]
        #         },
        #         "properties": {
        #             "time": curr_time.isoformat()
        #         }
        #     }, {
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [next_sat_pos.longitude.degrees, next_sat_pos.latitude.degrees, next_sat_pos.elevation.m]
        #         },
        #         "properties": {
        #             "time": (curr_time + timedelta(seconds=delta_time_sim)).isoformat()
        #         }
        #     }
        #     ]
        # }

        # Loop through fires that haven't started
        new_undetected_fires = []
        for fire in future_fires:
            # Check if fire should start this loop
            if start_time + fire.det_time < curr_time and fire not in active_fires:
                # Create GeoJSON point object of fire
                geo_fire = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [fire.pos.longitude.degrees, fire.pos.latitude.degrees]
                    }
                }
                # Adds GeoJSON to list of newly started fires
                new_undetected_fires.append(geo_fire)
                print(new_undetected_fires)
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
                geo_fire = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [fire.pos.longitude.degrees, fire.pos.latitude.degrees]
                    }
                }
                # Adds GeoJSON to list of newly detected fires
                new_detected_fires.append(geo_fire)
                # Adds Fire object to list of all detected fires
                detected_fires.append(fire)
                # Removes newly detected Fire object from list of all undetected fires
                undetected_fires.remove(fire)

        # To determine how long to wait between publications
        loop_end = datetime.now()

        # Sleep for the remaining time until the next publish time
        if pub_frequency >= (loop_end - loop_begin).total_seconds():
                time.sleep(pub_frequency - (loop_end - loop_begin).total_seconds())

        # Print and publish the current time
        print(f"time: {curr_time.isoformat()}")
        client.publish("pits/time", curr_time.isoformat())

        # Print and publish the satellite position
        print(f'pos: {geo_pos}')
        client.publish("pits/position", payload=json.dumps(geo_pos))

        # Loop through the new active fires and print and publish them individually
        for geo_fire in new_undetected_fires:
            print(f"active: {str(geo_fire)}")
            client.publish("pits/active_fires", payload=json.dumps(geo_fire))

        # Loop through the new detected fires and print and publish them individually
        for geo_fire in new_detected_fires:
            print(f"detected: {str(geo_fire)}")
            client.publish("pits/detected_fires", payload=json.dumps(geo_fire))

        # Increment simulation time and publish time
        curr_time += timedelta(seconds=delta_time_sim)
        pub_time += timedelta(seconds=pub_frequency)

        # Checks if all fires have been detected and end the sim if they have been
        if len(detected_fires) == num_of_fires:
            sim_end = datetime.now()
            print(f"Speed: {(sim_end - sim_start).total_seconds()}")

            time.sleep(2)   
            break

    client.loop_stop()


if __name__ == '__main__':
    main()