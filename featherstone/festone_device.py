import socket
import logging
import json

from typing import Dict

from .festone_protocol import (
	FestoneProtocol,
	FESTONE_PORT
)

_LOGGER = logging.getLogger(__name__)

class FestoneDevice():
	# The MAC address uniquely identifies the device
	def __init__(self, ip, uid):
		self.ip_addr = ip
		self.uid = uid
		self.password = ""
		self.protocol = FestoneProtocol()
		self.state = False
		
	def set_password(self, password: str):
		self.password = password
		
	def send_query(self, query):
		query["password"] = self.password
		query["device_uid"] = self.uid
		request_dump = json.dumps(query)
		encrypted_request = self.protocol.encrypt(request_dump)
		return self.protocol.query(self.ip_addr, encrypted_request)
		
	@property
	def device_id(self):
		raise NotImplementedError()
	@property
	def device_name(self):
		raise NotImplementedError()
	@property
	def device_addr(self):
		return self.ip_addr
	@property
	def device_uid(self):
		return self.uid
	@property
	def device_state(self):
		return self.state

	def update(self):
		raise NotImplementedError()
		
class FestoneRelay(FestoneDevice):
	DEVICE_ID = 0x1000
	DEVICE_NAME = "Relay"
	
	SET_QUERY = {
		"command": "set",
		"password": "",
		"device_uid": 0
	}
	RESET_QUERY = {
		"command": "reset",
		"password": "",
		"device_uid": 0
	}
	TOGGLE_QUERY = {
		"command": "toggle",
		"password": "",
		"device_uid": 0
	}
	GET_STATE_QUERY = {
		"command": "get_state",
		"password": "",
		"device_uid": 0
	}

	def __init__(self, ip, uid):
		FestoneDevice.__init__(self, ip=ip, uid=uid)
		
	@property
	def device_id(self):
		return self.DEVICE_ID
	@property
	def device_name(self):
		return self.DEVICE_NAME
		
	def set_relay(self):
		query = FestoneRelay.SET_QUERY
		_LOGGER.debug(
			"Sending set command to {0}:{1}".format(
				self.ip_addr, FESTONE_PORT
			)
		)
		response = self.send_query(query)
		if response:
			if response["command"] == "action_ok" and response["device_uid"] == self.uid:
				return True
		return False

	def reset_relay(self):
		query = FestoneRelay.RESET_QUERY
		_LOGGER.debug(
			"Sending reset command to {0}:{1}".format(
				self.ip_addr, FESTONE_PORT
			)
		)
		response = self.send_query(query)
		if response:
			if response["command"] == "action_ok" and response["device_uid"] == self.uid:
				return True
		return False

	def toggle_relay(self):
		query = FestoneRelay.TOGGLE_QUERY
		_LOGGER.debug(
			"Sending toggle command to {0}:{1}".format(
				self.ip_addr, FESTONE_PORT
			)
		)
		response = self.send_query(query)
		if response:
			if response["command"] == "action_ok" and response["device_uid"] == self.uid:
				return True
		return False
		
	def get_state(self):
		query = FestoneRelay.GET_STATE_QUERY
		_LOGGER.debug(
			"Sending get state command to {0}:{1}".format(
				self.ip_addr, FESTONE_PORT
			)
		)
		response = self.send_query(query)
		if response:
			if (response["command"] == "get_state" and 
					response["device_uid"] == self.uid and 
					"state" in response):
				return True, response["state"]
		return False, False

	def update(self):
		status, state = self.get_state()
		if status:
			self.state = state
			return True
		else:
			_LOGGER.error("Device {0} {1} did not response to get_state".format(self.device_name, self.device_uid))
			return True
