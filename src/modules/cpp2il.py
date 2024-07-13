import os
import subprocess
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
		self.processors = ["attributeanalyzer", "attributeinjector", "callanalyzer", "nativemethoddetector"]
		self.args = [
			"--verbose",
			"--use-processor", ','.join(self.processors),
			"--wasm-framework-file", f'{API.path}/framework.js',
			"--force-binary-path", f'{API.path}/game.wasm',
			"--force-metadata-path", f'{API.path}/WebData/Il2CppData/Metadata/global-metadata.dat',
			"--force-unity-version", "2022.2.5",
			"--output-to", f'{API.path}/CPP2IL',
		]

		self.__ensure_downloaded()
		API.cpp2il_path = API.cpp2il_path if os.name == "posix" else f"{API.cpp2il_path}/Cpp2IL.exe"

	def __ensure_downloaded(self):
		# setup cpp2il folder (just incase)
		os.makedirs(API.cpp2il_path, exist_ok=True)

		# download cpp2il if it hasn't been downloaded already
		if (
			(os.name == "nt" and os.path.exists(f"{API.cpp2il_path}/Cpp2IL.exe")) or
			(os.name == "posix" and os.path.exists(API.cpp2il_path))
		):
			logger.info("Found CPP2IL path.")
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
		logger.info('Generating Diffable C# files')
		output = subprocess.run([
			API.cpp2il_path,
			*self.args,
			'--output-as', 'diffable-cs'
		], capture_output=API.silent)

		# error handling
		if output.returncode == 0:
			logger.success('Diffable C# files generated!\n')
		else:
			logger.error('An error likely occurred during the generation of diffable-cs files.\n')
			if (output.stderr):
				print(output.stderr.decode('utf-8').splitlines()[-15:])

	def wasm_mappings(self):
		logger.info('Generating WASM mappings')
		output = subprocess.run([
			API.cpp2il_path,
			*self.args,
			'--output-as', 'wasmmappings'
		], capture_output=API.silent)

		# error handling
		if output.returncode == 0:
			logger.success('WASM mappings generated!\n')
		else:
			logger.error('An error likely occurred during the generation of the WASM Mappings.\n')
			if (output.stderr):
				print(output.stderr.decode('utf-8').splitlines()[-15:])

		# fixing the wasm mappings by splitting them into individual files
		# this is because cpp2il returns it into a single file for some reason??
		# it's split by comments saying the current dll name, so we can just split by that & don't write empty ones
		logger.info('Splitting WASM mappings into individual files')
		os.makedirs(f'{API.path}/CPP2IL/WASM Mappings', exist_ok=True)

		if os.path.exists(f'{API.path}/CPP2IL/wasm_mappings.txt'):
			with open(f'{API.path}/CPP2IL/wasm_mappings.txt', 'r') as f:
				mappings = f.read()
				mappings = mappings.replace('.dll\n\n', '.dll\n').split('\n\n\n') # just a way to get the list of mappings due to how its formatted

				for dll in mappings:
					methods = dll.split('\n') # split it per newline to get all methods
					if len(methods) == 1:
						continue

					name = os.path.splitext(methods[0])[0] # get dll name (w/o extension)
					with open(f'{API.path}/CPP2IL/WASM Mappings/{name}.txt', 'w') as f:
						f.write('\n'.join(methods[1:]))

			# os.remove(f'{API.path}/CPP2IL/wasm_mappings.txt')

		logger.success('Finished splitting WASM mappings!\n')
