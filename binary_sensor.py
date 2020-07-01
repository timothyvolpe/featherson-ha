import asyncio
import logging

from .const import(
	DOMAIN,
	FESTONE_MANAGER,
	FESTONE_DEVICE_DATA
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
	manager = hass.data[DOMAIN][config_entry.entry_id][FESTONE_MANAGER]
	device_data = hass.data[DOMAIN][config_entry.entry_id][FESTONE_DEVICE_DATA]
	
	binary_devices = [
		FestoneBinaryDevice(device)
		for device in device_data
	]
	
	async_add_entities(binary_devices)
	
class FestoneBinaryDevice(BinarySensorEntity):
	def __init__(self, device):
		self._name = device.device_name
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
