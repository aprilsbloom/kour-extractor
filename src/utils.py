import os
import random
import string

def random_string(length: int) -> str:
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class API:
	uuid: str = random_string(4)
	version: str
	path: str

	@staticmethod
	def setup_directory():
		API.path = f'output/{API.version} ({API.uuid})'
		os.makedirs(API.path, exist_ok=True)