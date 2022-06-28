import numpy as np


class Earth:
    def __init__(self):
        theta, phi = np.linspace(0, 2 * np.pi, 13), np.linspace(0, np.pi, 7)
        THETA, PHI = np.meshgrid(theta, phi)
        R = 6378
        self.x = R * np.sin(PHI) * np.cos(THETA)
        self.y = R * np.sin(PHI) * np.sin(THETA)
        self.z = R * np.cos(PHI)

