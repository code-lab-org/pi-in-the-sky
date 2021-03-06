from datetime import datetime
import json
import numpy as np
from pytz import timezone

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from skyfield.api import load, wgs84
from skyfield.framelib import itrs

from earth import Earth

# Pulls TLEs from celestrak
stations_url = 'http://celestrak.com/NORAD/elements/noaa.txt'
satellites = load.tle_file(stations_url, reload=True)
by_name = {sat.name: sat for sat in satellites}
satellite = by_name['SUOMI NPP [+]']

# The base object necessary to create and convert between
# different time formats
ts = load.timescale()

# The Time object storing when the TLE was most accurate
epoch = satellite.epoch
eastern = timezone('US/Eastern')
print(f'The most recent epoch is: \nUTC: {epoch.utc_datetime()} \n ET: {epoch.astimezone(eastern)}')

# Creates a Time object containing 100 time values over 100 minutes,
# 50 mintues before and after the latest epoch.
length = 100
time_range_epoch = ts.utc(epoch.utc.year, epoch.utc.month, epoch.utc.day, \
    epoch.utc.hour, range(epoch.utc.minute - int(length / 2), \
    epoch.utc.minute + int(length / 2), 1))

# Generates Geocentric inertial position objects over the time range
positions = satellite.at(time_range_epoch)

# Converts the above inertial position objects into a list containing
# three lists of ECEF x, y, and z coordinates in km.
xyz_pos = positions.frame_xyz(itrs).km

# Generates a dictionary containing latitude, longitiude, and elevation at each timestep
suomi = {}
dis_avg = 0
for pos_i, pos in enumerate(positions):
    lat = wgs84.geographic_position_of(pos).latitude
    lon = wgs84.geographic_position_of(pos).longitude
    dis = wgs84.geographic_position_of(pos).elevation

    suomi[str(pos_i)] = {'lat': lat.degrees, 'lon': lon.degrees, 'el': dis.km}
    dis_avg += dis.km

# GeographicPosition object of Hoboken
hoboken = wgs84.latlon(40.745255, -74.034775)
hob_x, hob_y, hob_z = hoboken.itrs_xyz.km
# Initalized plot and makes it 3D
fig = plt.figure()
ax = plt.axes(projection='3d')

# Plots path of satellite over 100 minutes
ax.plot3D(xyz_pos[0], xyz_pos[1], xyz_pos[2], 'red')

# Plots hoboken
ax.scatter3D(hob_x, hob_y, hob_z, color='green')

# Plots Earth
earth = Earth()
ax.plot_wireframe(earth.x, earth.y, earth.z, rstride=1, \
    cstride=1, color='black')
plt.show()

# Converts suomi dictionary to json and writes to file
with open('suomi.json', 'w') as i:
    json.dump(suomi, i)