import asyncio
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import(
	DOMAIN,
	FESTONE_MANAGER,
	FESTONE_DEVICE_DATA,
	FESTONE_DEVICE_UPDATE
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
	manager = hass.data[DOMAIN][config_entry.entry_id][FESTONE_MANAGER]
	device_data = hass.data[DOMAIN][config_entry.entry_id][FESTONE_DEVICE_DATA]

	_LOGGER.debug("Setting up binary sensors...")

	binary_devices = []
	for device in device_data.values():
		binary_devices.append(FestoneBinaryDevice(device))
		_LOGGER.debug("Creating entity for device {0}".format(device.device_name))
	
	#binary_devices = [
	#	FestoneBinaryDevice(device)
	#	for device in device_data
	#]
	
	async_add_entities(binary_devices)
	
class FestoneBinaryDevice(BinarySensorEntity):
	def __init__(self, device):
		self._name = "{0}_{1}".format(device.device_name,device.device_uid)
		self._id = device.device_id
		self._unique_id = device.device_uid
		self._state = None

	@property
	def is_on(self):
		# Return true if the binary sensor is on.
		return self._state

	@property
	def name(self):
		# Return the name of the binary sensor.
		return self._name

	@property
	def unique_id(self):
		# Return the unique id of the binary sensor.
		return self._unique_id

	async def async_added_to_hass(self):
		self.async_on_remove(
			async_dispatcher_connect(
				self.hass,
				FESTONE_DEVICE_UPDATE,
				self._async_update_from_data,
			)
		)

	@callback
	def _async_update_from_data(self):
		self._state = device.state
		self.async_write_ha_state()
