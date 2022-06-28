from skyfield.api import load, wgs84
from skyfield.framelib import itrs
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# Download all station TLEs from Celestrak, filter for only the ISS
stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url, reload=True)
by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(f'The most recent ISS epoch is: {satellite.epoch.utc_jpl()}')
print()

ts = load.timescale()
epoch = satellite.epoch
now = ts.now().utc
pos_epoch = satellite.at(epoch).frame_xyz(itrs).km
ISSorbit = 2 * np.pi / satellite.model.no_kozai
hoboken = wgs84.latlon(40.745255, -74.034775)
length =  4 *ISSorbit

time_range_epoch = ts.utc(epoch.utc.year, epoch.utc.month, epoch.utc.day, epoch.utc.hour, range(epoch.utc.minute - int(length / 2), epoch.utc.minute + int(length / 2), 1))
time_range_now = ts.utc(now.year, now.month, now.day, now.hour, range(now.minute - int(length / 2), now.minute + int(length / 2), 1))
pos_iss = satellite.at(time_range_epoch).frame_xyz(itrs).km

epoch_x, epoch_y, epoch_z = pos_epoch
iss_x, iss_y, iss_z = pos_iss

theta, phi = np.linspace(0, 2 * np.pi, 13), np.linspace(0, np.pi, 7)
THETA, PHI = np.meshgrid(theta, phi)
R = 6378
earth_x = R * np.sin(PHI) * np.cos(THETA)
earth_y = R * np.sin(PHI) * np.sin(THETA)
earth_z = R * np.cos(PHI)

fig = plt.figure()
ax = plt.axes(projection='3d')

ax.scatter3D(epoch_x, epoch_y, epoch_z, color='blue')
ax.plot3D(iss_x, iss_y, iss_z, 'red')
ax.plot_wireframe(earth_x, earth_y, earth_z, rstride=1, \
    cstride=1, color='black')
plt.show()