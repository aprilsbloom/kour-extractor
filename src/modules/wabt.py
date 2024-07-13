from logger import Logger
from typing import Final

logger = Logger("WABT")
class WABT():
	WABT_REPO: Final[str] = 'https://api.github.com/repos/WebAssembly/wabt/releases/latest'
	WABT_VERSION_REGEX: Final[str] = r'download\/([0-9.]+)'

	def __init__(self) -> None:
		pass

	def to_wat(self):
		pass

	def decompile(self):
		pass