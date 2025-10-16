"""Custom types for MyFuelPortal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.storage import Store
    from homeassistant.loader import Integration

    from .api import MyFuelPortalApiClient
    from .coordinator import MyFuelPortalDataUpdateCoordinator


type MyFuelPortalConfigEntry = ConfigEntry[MyFuelPortalData]
type MyFuelPortalCookieStorage = Store[dict]


@dataclass
class MyFuelPortalData:
    """Data for the MyFuelPortal integration."""

    client: MyFuelPortalApiClient
    coordinator: MyFuelPortalDataUpdateCoordinator
    integration: Integration
    cookies: MyFuelPortalCookieStorage
