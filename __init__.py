import asyncio
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from . import featherstone
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.const import(
	CONF_USERNAME, CONF_PASSWORD
)
from .const import(
	DOMAIN,
	FESTONE_MANAGER,
	FESTONE_DEVICE_DATA,
	FESTONE_DEVICE_UPDATE,
	FESTONE_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor"]

class FestoneDeviceData:
	def __init__(self):
		self._device_data = {}

CONFIG_SCHEMA = vol.Schema(
	{
		DOMAIN: vol.Schema(
			{
				vol.Required(CONF_USERNAME): cv.string,
				vol.Required(CONF_PASSWORD): cv.string,
			}
		)
	},
	extra = vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
	hass.data.setdefault(DOMAIN, {})
	conf = config.get(DOMAIN)
	if not conf:
		return True
	return true

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
	manager = featherstone.FestoneManager()

	# get devices
	device_data = FestoneDeviceData()
	discovered = featherstone.FestoneDiscover.discover_multiple()

	hass.data[DOMAIN][entry.entry_id] = {
		FESTONE_MANAGER: manager,
		FESTONE_DEVICE_DATA: discovered
	}

	for component in PLATFORMS:
		hass.async_create_task(
		hass.config_entries.async_forward_entry_setup(entry, component)
	)

	async def async_festone_update(_):
		_LOGGER.debug("Updating featherstone...")
		devices = hass.data[DOMAIN][entry.entry_id][FESTONE_DEVICE_DATA]
		for device in devices.values():
			device.update()
		async_dispatcher_send(hass, FESTONE_DEVICE_UPDATE)

	hass.data[DOMAIN][entry.entry_id][
		"track_time_remove_callback"
	] = async_track_time_interval(
		hass, async_festone_update, timedelta(seconds=FESTONE_UPDATE_INTERVAL)
	)

	return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
	unload_ok = all(
		await asyncio.gather(
			*[
				hass.config_entries.async_forward_entry_unload(entry, component)
				for component in PLATFORMS
			]
		)
	)
	track_time_remove_callback = hass.data[DOMAIN][entry.entry_id][
		"track_time_remove_callback"
	]

	if unload_ok:
		hass.data[DOMAIN].pop(entry.entry_id)

	return unload_ok
