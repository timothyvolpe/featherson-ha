import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
	pass
	
class FestoneBinaryDevice(BinarySensorEntity):
	def __init__(self, device):
		pass