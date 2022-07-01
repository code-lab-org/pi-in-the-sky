import numpy as np

from skyfield.api import load, wgs84
from skyfield.framelib import itrs

ts = load.timescale()
swath = 3000
elevation = 838.6
earth_rad = 6378
lmbda = np.pi * (swath / (2 * np.pi * earth_rad))
rho = np.arcsin(earth_rad / (earth_rad + elevation))
nu = np.arctan((np.sin(rho) * np.sin(lmbda)) / (1 - np.sin(rho) * np.cos(lmbda)))
epsilon_rad = np.pi / 2 - nu - lmbda
epsilon_deg = epsilon_rad * 180 / np.pi


def detect(satellite_pos, fire_pos):

    rel_pos = satellite_pos - fire_pos
    alt, az, distance = rel_pos.altaz()

    # Checks if altitude is above 30 dgerees
    if alt.degrees > epsilon_deg:
        return True

    return False


print(wgs84.latlon(0, 0, 0).at(ts.now()))