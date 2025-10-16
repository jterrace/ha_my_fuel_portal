import contextlib
import datetime
import importlib.resources
import re
from re import Pattern

from bs4 import BeautifulSoup

from . import testdata

_TANK_SIZE_RE = re.compile(r"(\d+)\ gal\.")
_TANK_REMAINING_RE = re.compile(r"(\d+)\ gallons\ in\ tank")
_PRICE_RE = re.compile(r"\$.*")
_LAST_DELIVERY_DATE_RE = re.compile(
    r"Last\ Delivery:\s*(\d{1,2}/\d{1,2}/\d{4})", re.MULTILINE
)
_NEXT_DELIVERY_DATE_RE = re.compile(
    r"Estimated\ Next\ Delivery:\s*(\d{1,2}/\d{1,2}/\d{4})", re.MULTILINE
)
_DATA_LAST_READ_DATE_RE = re.compile(
    r"Reading\ Date:\s*(\d{1,2}/\d{1,2}/\d{4})", re.MULTILINE
)


def _get_page(fname: str) -> str:
    data = importlib.resources.files(testdata).joinpath(fname).read_text()
    return BeautifulSoup(data, features="lxml")


def _get_numeric_regex(page: BeautifulSoup, pattern: Pattern) -> int | None:
    str_value = page.find(string=pattern)
    if not str_value:
        return None
    match = pattern.search(str_value)
    if not match:
        return None
    with contextlib.suppress(ValueError):
        return int(match.group(1))
    return None


def _get_price(page: BeautifulSoup) -> float | None:
    price_element = page.find("span", string=_PRICE_RE)
    if not price_element:
        return None
    with contextlib.suppress(ValueError):
        return float(price_element.text.lstrip("$"))
    return None


def _get_delivery_mode(page: BeautifulSoup) -> str | None:
    mode_element = page.find("div", class_="text-2")
    if not mode_element or mode_element.text not in ("Monitored", "Automatic"):
        return None
    return mode_element.text


def _get_date_regex(page: BeautifulSoup, pattern: Pattern) -> datetime.date | None:
    date_str = page.find(string=pattern)
    if not date_str:
        return None
    match = pattern.search(date_str)
    if not match:
        return None
    with contextlib.suppress(ValueError):
        return datetime.datetime.strptime(match.group(1), "%m/%d/%Y").date()
    return None


def _parse(page: BeautifulSoup) -> dict:
    box = page.find("div", class_="box-body")
    return {
        "tank_size": _get_numeric_regex(box, _TANK_SIZE_RE),
        "fuel_remaining": _get_numeric_regex(box, _TANK_REMAINING_RE),
        "price": _get_price(box),
        "delivery_mode": _get_delivery_mode(box),
        "last_delivery": _get_date_regex(box, _LAST_DELIVERY_DATE_RE),
        "next_delivery": _get_date_regex(box, _NEXT_DELIVERY_DATE_RE),
        "data_last_read": _get_date_regex(box, _DATA_LAST_READ_DATE_RE),
    }


def test_sample_1():
    assert _parse(_get_page("sample1.html")) == {
        "tank_size": 240,
        "fuel_remaining": 118,
        "price": 3.809,
        "delivery_mode": "Monitored",
        "last_delivery": datetime.date(2024, 12, 22),
        "next_delivery": None,
        "data_last_read": datetime.date(2025, 1, 5),
    }


def test_sample_2():
    assert _parse(_get_page("sample2.html")) == {
        "tank_size": 240,
        "fuel_remaining": 181,
        "price": 2.299,
        "delivery_mode": "Automatic",
        "last_delivery": datetime.date(2025, 1, 3),
        "next_delivery": datetime.date(2025, 2, 1),
        "data_last_read": None,
    }
