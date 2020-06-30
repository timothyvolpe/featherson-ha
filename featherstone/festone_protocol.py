import struct
import socket
import json

FESTONE_PORT = 6323

CIPHER_KEY_START = 111

class FestoneProtocol:
	@staticmethod
	def query(addr:str, encrypted_request, port: int=FESTONE_PORT, timeout: int=3):
		sock = None
		try:
			sock = socket.create_connection((addr, port), timeout)
			
			# Send the command
			sock.send(encrypted_request)
			
			# Wait for response length
			length_bytes = sock.recv(4)
			packet_length = 0
			if len(length_bytes) == 4:
				packet_length = struct.unpack("<I", length_bytes)[0]

				# Read the packet
				payload_bytes = sock.recv(packet_length)
				if len(payload_bytes) == packet_length:
					full_packet = length_bytes + payload_bytes;
					decrypted_data = FestoneProtocol.decrypt(payload_bytes)
					jsonData = json.loads(decrypted_data)
					if "command" in jsonData and "device_uid" in jsonData:
						return jsonData
		except socket.timeout:
			return None
		except json.JSONDecodeError as err:
			_LOGGER.error("Device at {0} responded, but the JSON packet was invalid: {1}".format(addr, err))
			return None
		finally:
			try:
				if sock:
					sock.shutdown(socket.SHUT_RDWR)
			except OSError:
				pass
			finally:
				if sock:
					sock.close()
				
		return None

	@staticmethod
	def encrypt(request: str) -> bytearray:
		current_key = CIPHER_KEY_START
		str_bytes = request.encode()
		# Append the length to the front
		byte_buffer = bytearray(struct.pack("<I", len(str_bytes)))
		for ch in str_bytes:
			encrypted = current_key ^ ch
			current_key = encrypted
			byte_buffer.append(encrypted)
		
		return bytes(byte_buffer)
		
	@staticmethod
	def decrypt(request: bytes) -> str:
		current_key = CIPHER_KEY_START
		str_bytes = []
		
		for ch in request:
			decrypted = current_key ^ ch
			current_key = ch
			str_bytes.append(decrypted)
			
		plaintext = bytes(str_bytes)
		
		return plaintext.decode()