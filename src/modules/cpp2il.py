import os
import subprocess
import zipfile
import requests
from logger import Logger
from typing import List

logger = Logger('CPP2IL')
WINDOWS_LINK = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-Netframework472-Windows.zip"
LINUX_LINK = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-net7-linux-x64.zip"

def run_cpp2il(state: dict):
	system_name = os.name

	# base state
	ensure_downloaded()
	path = "resources/Cpp2IL" if system_name == "posix" else "resources/cpp2il/Cpp2IL.exe"
	processors = ["attributeanalyzer", "attributeinjector", "callanalyzer", "nativemethoddetector", "stablenamer"]
	args = [
		"--verbose",
		"--use-processor", ','.join(processors),
		"--wasm-framework-file", f'{state["output_dir"]}/framework.js',
		"--force-binary-path", f'{state["output_dir"]}/kour.wasm',
		"--force-metadata-path", f'{state["output_dir"]}/WebData/Il2CppData/Metadata/global-metadata.dat',
		"--force-unity-version", "2023.2.5",
		"--output-to", f'{state["output_dir"]}/CPP2IL',
	]


	diffable_cs(path, args)
	wasm_mappings(state, path, args)

def ensure_downloaded():
	system_name = os.name

	# setup resources folder (just incase)
	os.makedirs("resources", exist_ok=True)

	# download cpp2il if it hasn't been downloaded already
	if (system_name == "nt" and not os.path.exists("resources/cpp2il/Cpp2IL.exe")) or (system_name == "posix" and not os.path.exists("resources/Cpp2IL")):
		logger.info("Downloading cpp2il!")

		# fetch the latest cpp2il release (nightly build)
		if system_name == "nt":
			r = requests.get(WINDOWS_LINK)
		elif system_name == "posix":
			r = requests.get(LINUX_LINK)
		else:
			logger.error("Unsupported OS! Cannot download CPP2IL.")
			return exit(1)

		with open("resources/cpp2il.zip", "wb") as f:
			f.write(r.content)

		logger.success("Downloaded cpp2il!")

		# extract the zip file
		logger.info("Extracting cpp2il")
		with zipfile.ZipFile("resources/cpp2il.zip", "r") as zip_ref:
			if system_name == "nt":
				os.makedirs("resources/cpp2il", exist_ok=True)
				zip_ref.extractall("resources/cpp2il")
			else:
				zip_ref.extractall("resources")

		logger.success("Extracted cpp2il!")
		os.remove("resources/cpp2il.zip")

		# ensure file is executable
		if system_name == "posix":
			os.system("chmod +x resources/Cpp2IL")


# ==== Methods ==== #
def diffable_cs(path: str, args: List[str]):
	logger.info('Generating Diffable C# files')
	output = subprocess.run([
		path,
		*args,
		'--output-as', 'diffable-cs'
	], capture_output=True)

	# if the return code is not 0, an error likely occurred
	if output.returncode != 0:
		logger.error('An error likely occurred during the generation of diffable-cs files.\n')
		print(output.stderr.decode('utf-8').splitlines()[-15:])
	else:
		logger.success('Diffable C# files generated!\n')

def wasm_mappings(state: dict, path: str, args: List[str]):
	logger.info('Generating WASM mappings')
	output = subprocess.run([
		path,
		*args,
		'--output-as', 'wasmmappings'
	], capture_output=True)

	# if the return code is not 0, an error likely occurred
	if output.returncode != 0:
		logger.error('An error likely occurred during the generation of wasm mappings.\n')
		print(output.stderr.decode('utf-8').splitlines()[-15:])
	else:
		logger.success('WASM mappings generated!\n')


	# fixing the wasm mappings by splitting them into individual files
	# this is because cpp2il returns it into a single file, for some reason??
	# it's split by comments saying the current dll name, so we can just split by that & don't write empty ones
	logger.info('Splitting WASM mappings into individual files')
	os.makedirs(f'{state["output_dir"]}/CPP2IL/WASM Mappings', exist_ok=True)

	if os.path.exists(f'{state["output_dir"]}/CPP2IL/wasm_mappings.txt'):
		with open(f'{state["output_dir"]}/CPP2IL/wasm_mappings.txt', 'r') as f:
			mappings = f.read()
			mappings = mappings.replace('.dll\n\n', '.dll\n').split('\n\n\n') # just a way to get the list of mappings due to how its formatted

			for dll in mappings:
				methods = dll.split('\n') # split it per newline to get all methods
				if len(methods) == 1:
					continue

				name = os.path.splitext(methods[0])[0] # get dll name (w/o extension)
				with open(f'{state["output_dir"]}/CPP2IL/WASM Mappings/{name}.txt', 'w') as f:
					f.write('\n'.join(methods[1:]))

		os.remove(f'{state["output_dir"]}/CPP2IL/wasm_mappings.txt')

	logger.success('Finished fixing WASM mappings!\n')