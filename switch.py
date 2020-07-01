import logging
import time

from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.components.switch import SwitchEntity

from .const import(
	DOMAIN,
	FESTONE_MANAGER,
	FESTONE_DEVICE_DATA,
	FESTONE_DEVICE_UPDATE,
	FESTONE_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

def add_entity(device, async_add_entities):
	async_add_entities([FestoneSwitch(device)], update_before_add=True)

async def async_setup_entry(hass: HomeAssistantType, config_entry, async_add_entities):
	manager = hass.data[DOMAIN][config_entry.entry_id][FESTONE_MANAGER]
	device_data = hass.data[DOMAIN][config_entry.entry_id][FESTONE_DEVICE_DATA]

	_LOGGER.debug("Setting up switches...")

	switch_devices = []
	for device in device_data.values():
		switch_devices.append(FestoneSwitch(device))
		_LOGGER.debug("Creating switch entity for device {0}".format(device.device_name))

	return True
	
class FestoneSwitch(SwitchEntity):
	def __init__(self, device):
		self._name = "{0}_{1}".format(device.device_name,device.device_uid)
		self._id = device.device_id
		self._unique_id = device.device_uid
		self._state = None
		self._device = device
		
	@property
	def name(self):
		# Return the name of the binary sensor.
		return self._name

	@property
	def unique_id(self):
		# Return the unique id of the binary sensor.
		return self._unique_id
		
	def turn_on(self, **kwargs):
        self._device.set_relay()

    def turn_off(self, **kwargs):
        self._device.reset_relay()
	