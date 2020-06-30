import asyncio
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import featherstone

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import(
	CONF_USERNAME, CONF_PASSWORD
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
	manager = FestoneManager()
	
	# get devices
	device_data = FestoneDeviceData()
	discovered = featherstone.FestoneDiscover.discover_multiple()
		
	