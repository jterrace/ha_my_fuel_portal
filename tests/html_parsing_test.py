import datetime
import importlib.resources

from bs4 import BeautifulSoup

from custom_components.ha_my_fuel_portal import parsing

from . import testdata


def _get_page(fname: str) -> str:
    data = importlib.resources.files(testdata).joinpath(fname).read_text()
    return BeautifulSoup(data, features="lxml")


def test_sample_1():
    assert parsing.parse_tank(_get_page("sample1.html")) == {
        "tank_size": 240,
        "fuel_remaining": 118,
        "price": 3.809,
        "delivery_mode": "Monitored",
        "last_delivery": datetime.date(2024, 12, 22),
        "next_delivery": None,
        "data_last_read": datetime.date(2025, 1, 5),
    }


def test_sample_2():
    assert parsing.parse_tank(_get_page("sample2.html")) == {
        "tank_size": 240,
        "fuel_remaining": 181,
        "price": 2.299,
        "delivery_mode": "Automatic",
        "last_delivery": datetime.date(2025, 1, 3),
        "next_delivery": datetime.date(2025, 2, 1),
        "data_last_read": None,
    }
