"""Routines for HTML parsing of the fuel portal site."""

import contextlib
import datetime
import re

import bs4

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


def _get_numeric_regex(page: bs4.BeautifulSoup, pattern: re.Pattern) -> int | None:
    str_value = page.find(string=pattern)
    if not str_value:
        return None
    match = pattern.search(str_value)
    if not match:
        return None
    with contextlib.suppress(ValueError):
        return int(match.group(1))
    return None


def _get_price(page: bs4.BeautifulSoup) -> float | None:
    price_element = page.find("span", string=_PRICE_RE)
    if not price_element:
        return None
    with contextlib.suppress(ValueError):
        return float(price_element.text.lstrip("$"))
    return None


def _get_delivery_mode(page: bs4.BeautifulSoup) -> str | None:
    mode_element = page.find("div", class_="text-2")
    if not mode_element or mode_element.text not in ("Monitored", "Automatic"):
        return None
    return mode_element.text


def _get_date_regex(
    page: bs4.BeautifulSoup, pattern: re.Pattern
) -> datetime.date | None:
    date_str = page.find(string=pattern)
    if not date_str:
        return None
    match = pattern.search(date_str)
    if not match:
        return None
    with contextlib.suppress(ValueError):
        return datetime.datetime.strptime(match.group(1), "%m/%d/%Y").date()
    return None


def parse_tank(page: bs4.BeautifulSoup) -> dict:
    """Parse the page to extract info about a tank."""
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
