from typing import Final

from logger import Logger

logger = Logger("WABT")
class WABT():
	WABT_REPO: Final[str] = 'https://api.github.com/repos/WebAssembly/wabt/releases/latest'
	WABT_VERSION_REGEX: Final[str] = r'download\/([0-9.]+)'

	def __init__(self) -> None:
		self.__ensure_downloaded()

	def __ensure_downloaded(self):
		pass

	def to_wat(self):
		pass

	def decompile(self):
		pass