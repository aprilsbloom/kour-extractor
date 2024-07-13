import os
from utils import random_string

from .setup import Setup
from .cpp2il import CPP2IL
from .wabt import WABT

class API:
	uuid: str = random_string(4)
	version: str
	path: str

	@staticmethod
	def setup_directory():
		API.path = f'output/{API.version} ({API.uuid})'
		os.makedirs(API.path, exist_ok=True)

__all__ = [
	"Setup",
	"CPP2IL",
	"WABT"
]