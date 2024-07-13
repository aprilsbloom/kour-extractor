import os
import requests
from zipfile import ZipFile
from typing import Final

from logger import Logger
from utils import API

logger = Logger("CPP2IL")
class CPP2IL():
	WINDOWS_LINK: Final[str] = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-Netframework472-Windows.zip"
	LINUX_LINK: Final[str] = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-net7-linux-x64.zip"

	def __init__(self) -> None:
		self.path = ''
		self.processors = ["attributeanalyzer", "attributeinjector", "callanalyzer", "nativemethoddetector"]
		self.args = [
			"--verbose",
			"--use-processor", ','.join(self.processors),
			"--wasm-framework-file", f'{self.path}/framework.js',
			"--force-binary-path", f'{self.path}/game.wasm',
			"--force-metadata-path", f'{self.path}/WebData/Il2CppData/Metadata/global-metadata.dat',
			"--force-unity-version", "2022.2.5",
			"--output-to", f'{self.path}/CPP2IL',
		]

		self.__ensure_downloaded()

	def __ensure_downloaded(self):
		# setup cpp2il folder (just incase)
		os.makedirs(API.cpp2il_path, exist_ok=True)

		# download cpp2il if it hasn't been downloaded already
		if (
			(os.name == "nt" and os.path.exists(f"{API.cpp2il_path}/Cpp2IL.exe")) or
			(os.name == "posix" and os.path.exists(API.cpp2il_path))
		):
			logger.info("CPP2IL already downloaded.")
			return

		logger.info("Downloading CPP2IL")

		# fetch the latest cpp2il release (nightly build)
		if os.name == "nt":
			r = requests.get(self.WINDOWS_LINK)
		elif os.name == "posix":
			r = requests.get(self.LINUX_LINK)
		else:
			logger.error("Unsupported OS! Cannot download CPP2IL.")
			return exit(1)

		# save & extract the zip file
		with open(f"{API.cpp2il_path}/cpp2il.zip", "wb") as f:
			f.write(r.content)

		logger.info("Extracting CPP2IL")
		with ZipFile(f"{API.cpp2il_path}/cpp2il.zip", "r") as zip:
			os.makedirs(API.cpp2il_path, exist_ok=True)
			zip.extractall(API.cpp2il_path)

		logger.success("Extracted cpp2il!\n")
		os.remove(f"{API.cpp2il_path}/cpp2il.zip")

		# ensure file is executable on linux
		if os.name == "posix":
			os.system(f"chmod +x {API.cpp2il_path}/Cpp2IL")


	def diffable_cs(self):
		pass

	def wasm_mappings(self):
		pass

