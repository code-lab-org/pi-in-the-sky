from skyfield.api import load, wgs84
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# Download all station TLEs from Celestrak, filter for only the ISS
stations_url = 'https://celestrak.com/NORAD/elements/supplemental/gps.txt'
satellites = load.tle_file(stations_url, reload=True)


ts = load.timescale()
now = ts.now().utc
ISSorbit = 92.68
hoboken = wgs84.latlon(40.745255, -74.034775)
length = 60*6

time_range = ts.utc(now.year, now.month, now.day, now.hour, range(now.minute - length, now.minute + length, 1))

now_positions = []
for sat in satellites:
    now_positions.append(sat.at(ts.now()).position.km)
print(now_positions)
positions = []
for sat in satellites:
    positions.append(sat.at(time_range).position.km)

tuple_positions = []
for position in positions:
    tuple_positions.append((position[0], position[1], position[2]))

theta, phi = np.linspace(0, 2 * np.pi, 13), np.linspace(0, np.pi, 7)
THETA, PHI = np.meshgrid(theta, phi)
R = 6378
X = R * np.sin(PHI) * np.cos(THETA)
Y = R * np.sin(PHI) * np.sin(THETA)
Z = R * np.cos(PHI)

fig = plt.figure()
ax = plt.axes(projection='3d')

for sat_i, sat in enumerate(tuple_positions):
    rel_pos = satellites[sat_i].at(ts.now()) - hoboken.at(ts.now())
    alt, az, distance = rel_pos.altaz()


    ax.plot3D(sat[0], sat[1], sat[2], 'red')
    if alt.degrees > 30:
        ax.plot3D((now_positions[sat_i][0], hoboken.at(ts.now()).position.km[0]), (now_positions[sat_i][1], hoboken.at(ts.now()).position.km[1]), (now_positions[sat_i][2], hoboken.at(ts.now()).position.km[2]), color='green')
        ax.scatter3D(now_positions[sat_i][0], now_positions[sat_i][1], now_positions[sat_i][2], color='yellow')
    else:
        ax.scatter3D(now_positions[sat_i][0], now_positions[sat_i][1], now_positions[sat_i][2], color='blue')
ax.scatter3D(hoboken.at(ts.now()).position.km[0], hoboken.at(ts.now()).position.km[1], hoboken.at(ts.now()).position.km[2], color='green')
ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1, color='black')
plt.show()




















