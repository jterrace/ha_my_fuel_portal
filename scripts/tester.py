import argparse
import asyncio
import json
import logging
import tempfile
from pathlib import Path

import mechanicalsoup

# ruff: noqa: T201, TRY003

logger = logging.getLogger(__name__)


class TankReadError(Exception):
    pass


def _get_cookie_path() -> str:
    return Path(tempfile.gettempdir()) / "temp-my-fuel-portal-cookies.json"


class TankFetcher:
    def __init__(self, username: str, password: str, tank_url: str):
        self.username = username
        self.password = password
        self.tank_url = tank_url

        self._browser = mechanicalsoup.StatefulBrowser()

    def _debug_print_page(self) -> None:
        print(self._browser.page.title.text, self._browser.url)

    def _load_tank_page(self) -> None:
        self._browser.open(self.tank_url)
        self._debug_print_page()

    def _login(self) -> None:
        self._browser.select_form(nr=0)
        self._browser["EmailAddress"] = self.username
        self._browser["Password"] = self.password
        self._browser.submit_selected()
        self._debug_print_page()

    def _save_cookies(self) -> None:
        cookies = dict(self._browser.get_cookiejar())
        with _get_cookie_path().open("w") as f:
            json.dump(cookies, f)

    def _load_cookies(self) -> None:
        try:
            with _get_cookie_path().open("r") as f:
                cookies = json.load(f)
                jar = self._browser.get_cookiejar()
                for name, value in cookies.items():
                    jar.set(name, value)
        except FileNotFoundError:
            return
        except json.decoder.JSONDecodeError:
            logger.exception("Failed to read json")

    def get(self) -> int:
        self._load_cookies()
        self._load_tank_page()

        if self._browser.url != self.tank_url:
            self._login()
            self._load_tank_page()

        if self._browser.url != self.tank_url:
            err = (
                f"Failed to fetch tank page {self.tank_url}. "
                f"Instead, wound up at {self._browser.url}."
            )
            raise TankReadError(err)

        progress = self._browser.page.find("div", class_="progress-bar")
        if progress is None:
            err = "Couldn't find progress bar div"
            raise TankReadError(err)

        try:
            progress = int(float(progress.attrs["aria-valuenow"]))
        except ValueError as e:
            err = "Failed to parse progress bar value {progress.attrs['aria-valuenow']}"
            raise TankReadError(err) from e

        self._save_cookies()

        return progress


async def main() -> int:
    parser = argparse.ArgumentParser(description="Test fetching tank data")
    parser.add_argument("--username", help="Username to log in", required=True)
    parser.add_argument("--password", help="Password to log in", required=True)
    parser.add_argument(
        "--tank_url",
        help="URL to access tank data",
        default="https://mysuperioraccountlogin.com/Tank",
    )
    args = parser.parse_args()

    #client = ha_my_fuel_portal.MyFuelPortalApiClient(
    #    args.username, args.password, args.tank_url
    #)
    #progress: int = await client.async_get_data()
    #print(progress)

    fetcher = TankFetcher(args.username, args.password, args.tank_url)
    print(fetcher.get())


if __name__ == "__main__":
    asyncio.run(main())
