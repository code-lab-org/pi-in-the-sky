from skyfield.api import load, wgs84
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# Download all station TLEs from Celestrak, filter for only the ISS
stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url, reload=True)
by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(f'The most recent ISS epoch is: {satellite.epoch.utc_jpl()}')

ts = load.timescale()
epoch = satellite.epoch
now = ts.now().utc
pos_epoch = satellite.at(epoch).position.km
ISSorbit = 92.68
hoboken = wgs84.latlon(40.745255, -74.034775)
length = int(ISSorbit)

time_range_epoch = ts.utc(epoch.utc.year, epoch.utc.month, epoch.utc.day, epoch.utc.hour, range(epoch.utc.minute - int(length), epoch.utc.minute + int(length), 1))
time_range_now = ts.utc(now.year, now.month, now.day, now.hour, range(now.minute - length, now.minute + length, 1))
ISSpos = satellite.at(time_range_now).position.km

x = ISSpos[0]
y = ISSpos[1]
z = ISSpos[2]

theta, phi = np.linspace(0, 2 * np.pi, 13), np.linspace(0, np.pi, 7)
THETA, PHI = np.meshgrid(theta, phi)
R = 6378
X = R * np.sin(PHI) * np.cos(THETA)
Y = R * np.sin(PHI) * np.sin(THETA)
Z = R * np.cos(PHI)

fig = plt.figure()
ax = plt.axes(projection='3d')

ax.scatter3D(pos_epoch[0], pos_epoch[1], pos_epoch[2], color='blue')
ax.plot3D(x, y, z, 'red')
ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1, color='black')
plt.show()