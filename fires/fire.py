import csv
import numpy as np
from skyfield.api import load, wgs84
from skyfield.framelib import itrs
from datetime import datetime


# Fire object that holds an id, geocetnricPosition, brightness, \
# and UTC Time object of detection
class Fire:
    def __init__(self, id, lat, lon, bright, date, time):
        self.id = id
        self.pos = wgs84.latlon(float(lat), float(lon))
        self.brightness = float(bright)
        mth, dy, yr = date.split('/')
        hr = int(time[:len(time)-2])
        min = int(time[len(time)-2:])
        self.det_time = load.timescale().utc(int(yr), int(mth), int(dy), hr, min)


# Pulls only the necessary columns from real fire csv
def parse_real_fires(columns=[0, 2, 3, 4, 7, 8]):
    with open('fires/new10kstart.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)

        fires = []
        for row in reader:
            fire = []
            for col in columns:
                fire.append(row[col])
            fires.append(fire)

        return fires


# Pulls only the necessary columns from fake fire csv
def parse_rand_fires(columns=[0, 1, 2, 3, 6, 7]):
    with open('fires/random_global_fires.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)

        fires = []
        for row in reader:
            fire = []
            for col in columns:
                fire.append(row[col])
            fires.append(fire)

        return fires


#
def getFires(str):
    if str == 'real':
        fires = parse_real_fires()
    elif str == 'fake':
        fires = parse_rand_fires()
    else:
        print("invalid")

    fire_obs = []
    for fire in fires:
        fire_obs.append(Fire(fire[0], fire[1], fire[2], fire[3] , \
            fire[4], fire[5]))

    return fire_obs