import datetime

from skyfield.api import load, wgs84
from skyfield.framelib import itrs

from backend.fires.fire import *


def test_parse_real():
    fires = parse_real_fires()
    assert fires[0] == ['0', '34.17638', '-85.761681', '297.01', datetime(2020, 1, 1, 7, 30)]
    assert fires[-1] == ['1027', '30.011585', '-81.730179', '326.29', datetime(2020, 1, 20, 17, 51)]


def test_parse_rand():
    fires = parse_rand_fires()
    assert fires[0] == ['0', '8.1231', '-68.88045', '297.01', datetime(2020, 1, 1, 7, 30)]
    assert fires[-1] == ['99', '6.29735', '-10.10458', '308.67', datetime(2020, 1, 1, 9, 12)]


def test_get_fires():
    real_fires = get_fires('real')
    random_fires = get_fires('random')

    assert real_fires[0].id == '0'
    assert str(real_fires[0].pos) == str(wgs84.latlon(34.17638, -85.761681))
    assert real_fires[0].brightness == 297.01
    assert real_fires[0].det_time == datetime(2020, 1, 1, 7, 30)

    assert real_fires[-1].id == '1027'
    assert str(real_fires[-1].pos) == str(wgs84.latlon(30.011585, -81.730179))
    assert real_fires[-1].brightness == 326.29
    assert real_fires[-1].det_time == datetime(2020, 1, 20, 17, 51)

    assert random_fires[0].id == '0'
    assert str(random_fires[0].pos) == str(wgs84.latlon(8.1231, -68.88045))
    assert random_fires[0].brightness == 297.01
    assert random_fires[0].det_time == datetime(2020, 1, 1, 7, 30)

    assert random_fires[-1].id == '99'
    assert str(random_fires[-1].pos) == str(wgs84.latlon(6.29735, -10.10458))
    assert random_fires[-1].brightness == 308.67
    assert random_fires[-1].det_time == datetime(2020, 1, 1, 9, 12)