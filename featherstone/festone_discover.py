"""
	The functionality offered in this file allows single or multiple devices
	to be discovered on the network.	
"""

import socket
import logging
import json

_LOGGER = logging.getLogger(__name__)

class FestoneDiscover:
	DEVICE_QUERY = {
		"hello"
	}

	@staticmethod
	def discover_multiple(
		protocol: FestoneProtocol = None,
		target_addr: str = "255.255.255.255",
        target_port: int = 9999,
        timeout: int = 3,
		packets_to_send: int = 3
		):
		
		# Create socket for broadcast
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
		
		# Encode the query
		if protocol is None:
			protocol = FestoneProtocol()
			
		# Send packets_to_send discovery queries
		request_dump = json.dumps(FestoneDiscover.DEVICE_QUERY)
		_LOGGER.debug("Sending discovery query to %s:%s", target_addr, target_port)
		encrypted_request = protocol.encrypt(request_dump)
		for i in range(packets_to_send):
			sock.sendto(encrypted_request, (target_addr, target_port))
		
		pass
	def discover_single():
		pass