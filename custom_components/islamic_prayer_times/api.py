"""Islamic Prayer api based on the api provided by https://aladhan.com/prayer-times-api."""

import asyncio
from datetime import timedelta
import logging

import async_timeout

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_METHOD, HTTP_OK
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_point_in_time
import homeassistant.util.dt as dt_util

from .const import (
    API_URL,
    CALC_METHODS,
    CONF_CALC_METHOD,
    CONF_LAT_ADJ_METHOD,
    CONF_MIDNIGHT_MODE,
    CONF_SCHOOL,
    DATA_UPDATED,
    DEFAULT_CALC_METHOD,
    DEFAULT_LAT_ADJ_METHOD,
    DEFAULT_MIDNIGHT_MODE,
    DEFAULT_SCHOOL,
    DOMAIN,
    FUTURE_DAYS,
    LAT_ADJ_METHODS,
    MIDNIGHT_MODES,
    SCHOOLS,
)

_LOGGER = logging.getLogger(__name__)


class IslamicPrayerApi:
    """Islamic Prayer Client Object."""

    def __init__(self, hass, config_entry):
        """Initialize the Islamic Prayer client."""
        self.hass = hass
        self.config_entry = config_entry
        self.today_prayer_times = {}
        self.weekly_prayer_times = {}
        self.available = True
        self.event_unsub = None

    @property
    def calc_method(self):
        """Return the calculation method."""
        return CALC_METHODS[
            self.config_entry.options.get(CONF_CALC_METHOD, DEFAULT_CALC_METHOD)
        ]

    @property
    def school(self):
        """Return the calculation school."""
        return SCHOOLS.index(self.config_entry.options.get(CONF_SCHOOL, DEFAULT_SCHOOL))

    @property
    def midnight_mode(self):
        """Return the midnight calculation method."""
        return MIDNIGHT_MODES.index(
            self.config_entry.options.get(CONF_MIDNIGHT_MODE, DEFAULT_MIDNIGHT_MODE)
        )

    @property
    def lat_adj_method(self):
        """Return the latitude adjutsment method."""
        return (
            LAT_ADJ_METHODS.index(
                self.config_entry.options.get(
                    CONF_LAT_ADJ_METHOD, DEFAULT_LAT_ADJ_METHOD
                )
            )
            + 1
        )

    async def async_get_new_prayer_times(self):
        """Return prayer times for selected dates."""

        prayer_times = {}
        prayer_times_all = []

        params = {
            CONF_LATITUDE: str(self.hass.config.latitude),
            CONF_LONGITUDE: str(self.hass.config.longitude),
            CONF_METHOD: self.calc_method,
            CONF_SCHOOL: self.school,
            CONF_MIDNIGHT_MODE: self.midnight_mode,
            CONF_LAT_ADJ_METHOD: self.lat_adj_method,
        }

        session = aiohttp_client.async_get_clientsession(self.hass)
        # i = 0
        for i in range(FUTURE_DAYS):
            date = dt_util.now().date() + timedelta(days=i)
            date_timestamp = dt_util.as_timestamp(date)
            try:
                with async_timeout.timeout(10):
                    response = await session.get(
                        f"{API_URL}/{int(date_timestamp)}", params=params
                    )

            except asyncio.TimeoutError:
                _LOGGER.error("%s is not responding", API_URL)
                raise ConnectionError

            if response.status != HTTP_OK:
                resp = await response.text()
                _LOGGER.warning("Error retrving information: %s", resp)
                return None

            # i += 1
            resp_json = await response.json()
            prayer_times = resp_json["data"]["timings"]
            _LOGGER.debug(prayer_times)

            for prayer, time in prayer_times.items():
                prayer_times[prayer] = dt_util.parse_datetime(f"{date} {time}")

            prayer_times_all.append(prayer_times)

        return prayer_times_all

    async def async_schedule_future_update(self):
        """Schedule future update for sensors.

        Midnight is a calculated time.  The specifics of the calculation
        depends on the method of the prayer time calculation.  This calculated
        midnight is the time at which the time to pray the Isha prayers have
        expired.

        Calculated Midnight: The Islamic midnight.
        Traditional Midnight: 12:00AM

        Update logic for prayer times:

        If the Calculated Midnight is before the traditional midnight then wait
        until the traditional midnight to run the update.  This way the day
        will have changed over and we don't need to do any fancy calculations.

        If the Calculated Midnight is after the traditional midnight, then wait
        until after the calculated Midnight.  We don't want to update the prayer
        times too early or else the timings might be incorrect.

        Example:
        calculated midnight = 11:23PM (before traditional midnight)
        Update time: 12:00AM

        calculated midnight = 1:35AM (after traditional midnight)
        update time: 1:36AM.

        """
        _LOGGER.debug("Scheduling next update for Islamic prayer times")

        now = dt_util.utcnow()

        midnight_dt = self.today_prayer_times["Midnight"]

        if now > dt_util.as_utc(midnight_dt):
            next_update_at = midnight_dt + timedelta(days=1, minutes=1)
            _LOGGER.debug(
                "Midnight is after day the changes so schedule update for after Midnight the next day"
            )
        else:
            _LOGGER.debug(
                "Midnight is before the day changes so schedule update for the next start of day"
            )
            next_update_at = dt_util.start_of_local_day(now + timedelta(days=1))

        _LOGGER.info("Next update scheduled for: %s", next_update_at)

        self.event_unsub = async_track_point_in_time(
            self.hass, self.async_update, next_update_at
        )

    async def async_update(self, *_):
        """Update sensors with new prayer times."""
        try:
            prayer_times = await self.async_get_new_prayer_times()
            self.available = True
        except ConnectionError:
            self.available = False
            _LOGGER.debug("Error retrieving prayer times.")
            async_call_later(self.hass, 60, self.async_update)
            return

        self.today_prayer_times = prayer_times.pop(0)
        self.weekly_prayer_times = prayer_times
        await self.async_schedule_future_update()

        _LOGGER.debug("New prayer times retrieved. Updating sensors.")
        async_dispatcher_send(self.hass, DATA_UPDATED)

    async def async_setup(self):
        """Set up the Islamic prayer client."""

        try:
            if not await self.async_get_new_prayer_times():
                return False
        except ConnectionError:
            raise ConfigEntryNotReady

        await self.async_update()
        self.config_entry.add_update_listener(self.async_options_updated)

        self.hass.async_create_task(
            self.hass.config_entries.async_forward_entry_setup(
                self.config_entry, "sensor"
            )
        )

        return True

    @staticmethod
    async def async_options_updated(hass, entry):
        """Triggered by config entry options updates."""
        if hass.data[DOMAIN].event_unsub:
            hass.data[DOMAIN].event_unsub()
        await hass.data[DOMAIN].async_update()
