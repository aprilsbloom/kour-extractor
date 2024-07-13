import re
import requests
from logger import Logger
from typing import Final

logger = Logger("Setup")
class Setup():
	BASE_DOMAIN: Final[str] = "https://kour.io"
	VERSION_REGEX: Final = r"productVersion:(?: |)\"([0-9.]+)"
	BUILD_REGEX: Final = r"buildUrl(?: |)=(?: |)(?:[a-zA-Z +\?]+)\"(?:[a-zA-Z:\/\-\.\ ]+)\"(?: |):(?: |)\"([a-zA-Z:\/\-\.\ ]+)"
	FRAMEWORK_REGEX: Final = r"frameworkUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
	WEB_DATA_REGEX: Final = r"dataUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
	WASM_REGEX: Final = r"codeUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""

	def __init__(self) -> None:
		pass

	def fetch_kour_files(self):
		self.html = self.__fetch_initial_page()
		self.version = self.__fetch_version()
		self.build_url = self.__fetch_build_url()

		self.framework = self.__fetch_framework()
		self.web_data = self.__fetch_web_data()
		self.wasm = self.__fetch_wasm()

	def __fetch_initial_page(self) -> str:
		logger.info("Fetching HTML from Kour.io")
		r = requests.get(self.BASE_DOMAIN)
		return r.text

	def __fetch_version(self) -> str:
		return re.findall(self.VERSION_REGEX, self.html)[0]

	def __fetch_build_url(self) -> str:
		return re.findall(self.BUILD_REGEX, self.html)[0]

	def __fetch_framework(self) -> str:
		url = self.build_url + re.findall(self.FRAMEWORK_REGEX, self.html)[0]
		r = requests.get(url)
		return r.text

	def __fetch_web_data(self) -> bytes:
		url = self.build_url + re.findall(self.WEB_DATA_REGEX, self.html)[0]
		r = requests.get(url)
		return r.content

	def __fetch_wasm(self) -> bytes:
		url = self.build_url + re.findall(self.WASM_REGEX, self.html)[0]
		r = requests.get(url)
		return r.content