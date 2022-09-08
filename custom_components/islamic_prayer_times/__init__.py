"""The islamic_prayer_times component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CALC_METHODS, CONF_CALC_METHOD, DOMAIN
from .coordinator import IslamicPrayerDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Islamic Prayer Component."""
    await async_update_options(hass, entry)
    coordinator = IslamicPrayerDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Islamic Prayer entry from config_entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: IslamicPrayerDataUpdateCoordinator = hass.data.pop(DOMAIN)
        if coordinator.event_unsub:
            coordinator.event_unsub()
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update calc_method option from old entry."""
    if old_calc_method := entry.options.get(CONF_CALC_METHOD):
        if old_calc_method not in CALC_METHODS:
            new_options = {**entry.options}
            for method in CALC_METHODS:
                if old_calc_method == method.lower():
                    new_options[CONF_CALC_METHOD] = method
                    break
            hass.config_entries.async_update_entry(
                entry,
                options={**entry.options, **new_options},
            )
