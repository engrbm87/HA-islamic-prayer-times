"""Platform to retrieve Islamic prayer times information for Home Assistant."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from . import IslamicPrayerDataCoordinator
from .const import DOMAIN, PRAYER_TIMES_ICON, SENSOR_TYPES


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Islamic prayer times sensor platform."""

    coordinator = hass.data[DOMAIN]

    entities = []
    for description in SENSOR_TYPES:
        entities.append(IslamicPrayerTimeSensor(coordinator, description))

    async_add_entities(entities)


class IslamicPrayerTimeSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Islamic prayer time sensor."""

    coordinator: IslamicPrayerDataCoordinator
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = PRAYER_TIMES_ICON
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: IslamicPrayerDataCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the Islamic prayer time sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "Islamic Prayer Times")},
            default_name="Islamic Prayer Times",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data[self.entity_description.key].astimezone(
            dt_util.UTC
        )
