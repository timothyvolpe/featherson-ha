
class FestoneProtocol:
	def encrypt(request: str) -> bytearray:
		str_bytes = str.encode();
		byte_buffer = bytearray(struct.pack(">I", len(str_bytes)))
		
		return bytes(byte_buffer)