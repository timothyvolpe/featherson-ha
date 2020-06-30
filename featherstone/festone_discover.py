"""
	The functionality offered in this file allows single or multiple devices
	to be discovered on the network.	
"""

import socket
import logging
import json
import ipaddress
import time

from typing import Dict

from .festone_protocol import (
	FestoneProtocol,
	FESTONE_PORT
)
from .festone_device import (
	FestoneDevice,
	FestoneRelay
)

_LOGGER = logging.getLogger(__name__)

NETMASK = '255.255.255.0'

class FestoneDiscover:
	DEVICE_QUERY = {
		"command": "discovery"
	}

	@staticmethod
	def discover_multiple(
		protocol: FestoneProtocol = None,
		target_addr: str = '<broadcast>',
		target_port: int = FESTONE_PORT,
		timeout: int = 3,
		packets_to_send: int = 3
		) -> Dict[str, FestoneDevice]:
		
		# Create socket for broadcast
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', 0))
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(timeout)

		if target_addr == '<broadcast>':
			# Determine broadcast address
			ip_addr = socket.gethostbyname(socket.gethostname())
			net = ipaddress.IPv4Network(ip_addr + '/' + NETMASK, False)
			broadcast_addr = str(net.broadcast_address)
			target_addr = broadcast_addr
		
		# Encode the query
		if protocol is None:
			protocol = FestoneProtocol()
			
		# Send packets_to_send discovery queries
		request_dump = json.dumps(FestoneDiscover.DEVICE_QUERY)
		_LOGGER.debug(
			"Sending discovery query to {0}:{1}".format(
				target_addr, target_port
			)
		)
		encrypted_request = protocol.encrypt(request_dump)
		for i in range(packets_to_send):
			sock.sendto(encrypted_request, (target_addr, target_port))
			
		discovered_devices = {}
		
		# Get any response
		try:
			while True:
				data, addr = sock.recvfrom(260)
				ip, port = addr
				decryptedData = protocol.decrypt(data[4:])
				jsonData = json.loads(decryptedData)
				# Attempt to get device class object
				if "command" in jsonData:
					if jsonData["command"] == "discovery_ok":
						if "device_id" in jsonData and "device_uid" in jsonData:
							device_class = FestoneDiscover.resolve_device_class(jsonData["device_id"])
							if device_class is not None:
								# found a valid device, initialize
								discovered_devices[ip] = device_class(ip, jsonData["device_uid"])
								pass
							else:
								_LOGGER.debug(
									"Device at {0} is not a supported device" \
									" (invalid device ID)".format(addr)
								)
						else:
							_LOGGER.debug(
								"Received invalid discovery-ok " \
								"command data from {0}".format(addr)
							)
					else:
						_LOGGER.debug(
							"Received invalid discovery command " \
							"from {0}".format(addr)
						)
				else:
					_LOGGER.debug(
						"Received invalid discovery packet " \
						"from {0}".format(addr)
					)
		except json.JSONDecodeError as err:
			_LOGGER.error("Device at {0} responded, but the JSON packet was invalid: {1}".format(addr, err))
		except socket.timeout:
			pass #
		except Exception as err:
			_LOGGER.error("Discovery exception {0}".format(err))
		
		try:
			if sock:
				sock.shutdown(socket.SHUT_RDWR)
		except OSError:
			pass
		finally:
			sock.close()
			
		return discovered_devices
			
	@staticmethod
	def discover_single():
		pass
		
	@staticmethod
	def resolve_device_class(device_id: int):
		if device_id == FestoneRelay.DEVICE_ID:
			return FestoneRelay
		else:
			return None
			
# main from command line
if __name__ == "__main__":
	print("Searching for featherstone devices...")
	
	devices = FestoneDiscover.discover_multiple()
	
	if not devices:
		print("No devices responded")
	
	for device in devices.values():
		print("Found a {0} at address {1} (UID: {2})".format(device.device_name, device.device_addr, device.device_uid))
	
		device.set_password("")
		print("Setting relay")
		if device.set_relay():
			print("Relay set command was successfully processed")
		else:
			print("Device did not process relay set command")
		time.sleep(1)
		print("Resetting relay")
		if device.reset_relay():
			print("Relay reset command was successfully processed")
		else:
			print("Device did not process relay reset command")
		time.sleep(1)
		
		print("Querying state")
		status, state = device.get_state()
		if status:
			print("Device state is: {0}".format(("set" if state else "reset")))
		else:
			print("Device did not process get state command")
		
		print("Toggling relay")
		if device.toggle_relay():
			print("Relay toggle command was successfully processed")
		else:
			print("Device did not process relay toggle command")
		time.sleep(1)