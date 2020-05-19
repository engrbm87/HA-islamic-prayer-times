"""The islamic_prayer_times component."""
import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT

from .api import IslamicPrayerApi
from .const import (
    CALC_METHODS,
    CONF_CALC_METHOD,
    CONF_LAT_ADJ_METHOD,
    CONF_MIDNIGHT_MODE,
    CONF_SCHOOL,
    DEFAULT_CALC_METHOD,
    DEFAULT_LAT_ADJ_METHOD,
    DEFAULT_MIDNIGHT_MODE,
    DEFAULT_SCHOOL,
    DOMAIN,
    LAT_ADJ_METHODS,
    MIDNIGHT_MODES,
    SCHOOLS,
)

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: {
            vol.Optional(CONF_CALC_METHOD, default=DEFAULT_CALC_METHOD): vol.In(
                CALC_METHODS
            ),
            vol.Optional(CONF_SCHOOL, default=DEFAULT_SCHOOL): vol.In(SCHOOLS),
            vol.Optional(CONF_MIDNIGHT_MODE, default=DEFAULT_MIDNIGHT_MODE): vol.In(
                MIDNIGHT_MODES
            ),
            vol.Optional(CONF_LAT_ADJ_METHOD, default=DEFAULT_LAT_ADJ_METHOD): vol.In(
                LAT_ADJ_METHODS
            ),
        }
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Import the Islamic Prayer component from config."""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
            )
        )

    return True


async def async_setup_entry(hass, config_entry):
    """Set up the Islamic Prayer Component."""
    client = IslamicPrayerApi(hass, config_entry)

    if not await client.async_setup():
        return False

    hass.data.setdefault(DOMAIN, client)
    return True


async def async_unload_entry(hass, config_entry):
    """Unload Islamic Prayer entry from config_entry."""
    if hass.data[DOMAIN].event_unsub:
        hass.data[DOMAIN].event_unsub()
    hass.data.pop(DOMAIN)
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

    return True
