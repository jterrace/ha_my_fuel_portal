# MyFuelPortal Home Assistant Custom Component

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Community Forum][forum-shield]][forum]

_[Integration][ha_my_fuel_portal] to integrate MyFuelPortal to monitor tanks._

**This integration will set up the following platforms.**

| Platform | Description |
| -------- | ----------- |
| `sensor` | TODO        |

## HACS Installation

TODO

## Manual Installation

Copy contents of `custom_components/ha_my_fuel_portal/` to `custom_components/ha_my_fuel_portal/` in your Home Assistant config folder.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Sensors

 - Tank size (gallons)
 - Fuel remaining (gallons)
 - Fuel price (dollars)
 - Fuel delivery mode (Monitored or Automated)
 - Last delivery date
 - Next delivery date (if fuel mode is automated)
 - Last data read date (if fuel mode is monitored)

## Development

### Setup

```
$ virtualenv venv
$ source ./venv/bin/activate
$ ./scripts/setup
```

### Running Tests

```
$ ./venv/bin/pytest tests
```

### Running hass

```
$ ./venv/bin/develop
```

***

[ha_my_fuel_portal]: https://github.com/jterrace/ha_my_fuel_portal
[commits-shield]: https://img.shields.io/github/commit-activity/y/jterrace/ha_my_fuel_portal.svg?style=for-the-badge
[commits]: https://github.com/jterrace/ha_my_fuel_portal/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/jterrace/ha_my_fuel_portal.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jterrace/ha_my_fuel_portal.svg?style=for-the-badge
[releases]: https://github.com/jterrace/ha_my_fuel_portal/releases
