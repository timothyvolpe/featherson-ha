import logging
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import(
	CONF_USERNAME, CONF_PASSWORD
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
	{
		vol.Required(CONF_USERNAME): str,
		vol.Required(CONF_PASSWORD): str,
	}
)

async def discover_device( hass: core.HomeAssistant, data ):
	return {"title": data[CONF_USERNAME]}
	
class FeatherstoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	async def async_step_user(self, user_input = None):
		errors = {}
		if user_input is not None:
			device_info = await discover_device(self.hass, user_input)
			await self.async_set_unique_id(user_input[CONF_USERNAME])
			return self.async_create_entry(title=device_info["title"], data=user_input)
			pass
		except Exception as err:
			_LOGGER.exception(
				"Exception validating credentials: {0}".format(err)
			)
			errors["base"] = "unknown"
		return self.async_show_form(
			step_id="user", data_schema=DATA_SCHEMA, errors=errors
		)
	async def async_step_import(self, user_input):
		await self.async_set_unique_id(user_input[CONF_USERNAME])
		self._abort_if_unique_id_configured()
		return await self.async_step_user( user_input )