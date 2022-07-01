from skyfield.api import load, wgs84
from skyfield.framelib import itrs

from ..detect import detect


def test_detect():
    ts = load.timescale()
    satellite_pos_true = wgs84.latlon(0, 0, 850).at(ts.now())
    satellite_pos_false = wgs84.latlon(90, 180, 850).at(ts.now())
    fire_pos = wgs84.latlon(0, 0, 0).at(ts.now())

    assert detect(satellite_pos_true, fire_pos) == True
    assert detect(satellite_pos_false, fire_pos) == False