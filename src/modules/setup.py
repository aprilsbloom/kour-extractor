import re
import requests
from uwdtool import UWDTool
from typing import Final

from utils import API
from logger import Logger


logger = Logger("Setup")
class Setup():
	BASE_DOMAIN: Final[str] = "https://kour.io"
	VERSION_REGEX: Final[str] = r"productVersion:(?: |)\"([0-9.]+)"
	BUILD_REGEX: Final[str] = r"buildUrl(?: |)=(?: |)(?:[a-zA-Z +\?]+)\"(?:[a-zA-Z:\/\-\.\ ]+)\"(?: |):(?: |)\"([a-zA-Z:\/\-\.\ ]+)"
	FRAMEWORK_REGEX: Final[str] = r"frameworkUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
	WEB_DATA_REGEX: Final[str] = r"dataUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
	WASM_REGEX: Final[str] = r"codeUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""

	def fetch_kour_files(self):
		self.html = self.__fetch_initial_page()
		self.version = self.__fetch_version()

		API.version = self.version
		API.setup_directory()

		self.build_url = self.__fetch_build_url()
		self.framework = self.__fetch_framework()
		self.web_data = self.__fetch_web_data()
		self.wasm = self.__fetch_wasm()

		with open(f'{API.path}/framework.js', 'w') as f:
			f.write(self.framework)

		with open(f'{API.path}/web.data', 'wb') as f:
			f.write(self.web_data)

		with open(f'{API.path}/game.wasm', 'wb') as f:
			f.write(self.wasm)

		self.__unpack_web_data()

	def __fetch_initial_page(self) -> str:
		logger.info("Fetching HTML from Kour.io")
		r = requests.get(self.BASE_DOMAIN)
		return r.text

	def __fetch_version(self) -> str:
		return re.findall(self.VERSION_REGEX, self.html)[0]

	def __fetch_build_url(self) -> str:
		return re.findall(self.BUILD_REGEX, self.html)[0]

	def __fetch_framework(self) -> str:
		logger.info("Fetching framework.js")
		url = self.build_url + re.findall(self.FRAMEWORK_REGEX, self.html)[0]
		r = requests.get(url)
		return r.text

	def __fetch_web_data(self) -> bytes:
		logger.info("Fetching WebData")
		url = self.build_url + re.findall(self.WEB_DATA_REGEX, self.html)[0]
		r = requests.get(url)
		return r.content

	def __unpack_web_data(self):
		logger.info("Unpacking WebData")
		unpacker = UWDTool.UnPacker()
		unpacker.unpack(f'{API.path}/web.data', f'{API.path}/WebData')  # unpacking

	def __fetch_wasm(self) -> bytes:
		logger.info("Fetching game.wasm")
		url = self.build_url + re.findall(self.WASM_REGEX, self.html)[0]
		r = requests.get(url)
		return r.content