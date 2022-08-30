import csv
from datetime import datetime, timedelta
import numpy as np
import json
import os

from skyfield.api import load, wgs84, utc
from skyfield.framelib import itrs


# Fire object that holds an id, geocetnricPosition, brightness, \
# and UTC Time object of detection
class Fire:
    def __init__(self, id, lat, lon, bright, date_time):
        self.id = id
        self.pos = wgs84.latlon(float(lat), float(lon))
        self.brightness = float(bright)
        self.det_time = date_time


# Pulls only the necessary columns from real fire csv
def parse_real_fires(columns=[0, 2, 3, 4, 7]):
    with open(f'{os.path.dirname(__file__)}/new10kstart.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)

        fires = []
        for row in reader:
            fire = []
            for col in columns:
                if col == 7:
                    mth, dy, yr = row[col].split('/')
                    hr = int(row[8][:len(row[8])-2])
                    min = int(row[8][len(row[8])-2:])
                    time_diff = timedelta(int(yr) - 2020, int(mth), int(dy), hr - 7, min - 30)
                    fire.append(time_diff)
                else:
                    fire.append(row[col])
            fires.append(fire)

        return fires


# Pulls only the necessary columns from fake fire csv
def parse_rand_fires(columns=[0, 1, 2, 3, 6]):
    with open(f'{os.path.dirname(__file__)}/random_global_fires.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)

        fires = []
        for row in reader:
            fire = []
            for col in columns:
                if col == 6:
                    mth, dy, yr = row[col].split('/')
                    hr = int(row[7][:len(row[7])-2])
                    min = int(row[7][len(row[7])-2:])
                    time_diff = timedelta(int(yr) - 2020, int(mth), int(dy), hr - 7, min - 30)
                    fire.append(time_diff)
                else:
                    fire.append(row[col])
            fires.append(fire)

        return fires


# Takes an input for which dataset to use, and returns a list of Fire
# objects for the data
def get_fires(str):
    assert str == "real" or "random"
    if str == 'real':
        fires = parse_real_fires()
    else:
        fires = parse_rand_fires()

    fire_obs = []
    for fire in fires:
        fire_obs.append(Fire(fire[0], fire[1], fire[2], fire[3] , \
            fire[4]))

    return fire_obs


def create_geojson(fires):

    fires_geojson = {"type": "Feature", \
                    "geometry": {
                        "type": "MultiPoint",
                        "coordinates": []}
                    }

    for fire in fires:
        fires_geojson['geometry']['coordinates'].append([float(fire[1]), float(fire[2])])

    return fires_geojson