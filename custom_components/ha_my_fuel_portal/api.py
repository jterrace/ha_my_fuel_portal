"""Sample API Client."""

from __future__ import annotations

import asyncio
import json
import socket
from typing import Any

import async_timeout
import mechanicalsoup


class MyFuelPortalApiClientError(Exception):
    """Exception to indicate a general API error."""


class MyFuelPortalApiClientCommunicationError(
    MyFuelPortalApiClientError,
):
    """Exception to indicate a communication error."""


class MyFuelPortalApiClientAuthenticationError(
    MyFuelPortalApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise MyFuelPortalApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class MyFuelPortalApiClient:
    """API Client for the fuel portal."""

    def __init__(
        self,
        username: str,
        password: str,
        url: str,
    ) -> None:
        """API Client for the fuel portal."""
        self._username = username
        self._password = password
        self._url = url

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
            progress = int(progress.attrs["aria-valuenow"])
        except ValueError as e:
            err = "Failed to parse progress bar value {progress.attrs['aria-valuenow']}"
            raise TankReadError(err) from e

        self._save_cookies()

        return progress

    async def async_get_data(self) -> int:
        """Get data from the API."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.get)

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise MyFuelPortalApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise MyFuelPortalApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise MyFuelPortalApiClientError(
                msg,
            ) from exception
