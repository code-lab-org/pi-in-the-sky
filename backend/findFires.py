import json
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from skyfield.api import load, wgs84
from skyfield.framelib import itrs

from earth import Earth
from fires.fire import Fire, getFires


Fires = getFires('fake')
ts = load.timescale()
f = open('suomi.json')
satellite = json.load(f)
positions = []
for pos in range(100):
    positions.append(wgs84.latlon(satellite[f'{pos}']['lat'],
        satellite[f'{pos}']['lon'], elevation_m=1000*satellite[f'{pos}']['el']))

swath = 3000
elevation = 838.6
earth_rad = 6378
lmbda = np.pi * (swath / (2 * np.pi * earth_rad))
rho = np.arcsin(earth_rad / (earth_rad + elevation))
nu = np.arctan((np.sin(rho) * np.sin(lmbda)) / (1 - np.sin(rho) * np.cos(lmbda)))
epsilon_rad = np.pi / 2 - nu - lmbda
epsilon_deg = epsilon_rad * 180 / np.pi

fig = plt.figure()
ax = plt.axes(projection='3d')

for fire in Fires:
    for sat_i, sat in enumerate(positions):
        # Find relative position of sat to Hoboken, calculate altitude, azimuth, and distance
        rel_pos = sat.at(ts.now()) - fire.pos.at(ts.now())
        alt, az, distance = rel_pos.altaz()
        # Checks if altitude is above 30 dgerees
        visible = False
        if alt.degrees > epsilon_deg:
            visible = True
            break
    if visible:
        fire_x, fire_y, fire_z = fire.pos.itrs_xyz.km
        ax.scatter3D(fire_x, fire_y, fire_z, color='green')
    else:
        fire_x, fire_y, fire_z = fire.pos.itrs_xyz.km
        ax.scatter3D(fire_x, fire_y, fire_z, color='red')

earth = Earth()
ax.plot_wireframe(earth.x, earth.y, earth.z, rstride=1, \
    cstride=1, color='black')

pos_x, pos_y, pos_z = [[], [], []]
for pos in positions:
    pos_x.append(pos.itrs_xyz.km[0])
    pos_y.append(pos.itrs_xyz.km[1])
    pos_z.append(pos.itrs_xyz.km[2])

ax.plot3D(pos_x, pos_y, pos_z, color='blue')
plt.show()