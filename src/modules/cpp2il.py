import json
import os
import subprocess
import zipfile
import requests
from logger import Logger
from utils import remove_arr_duplicates, remove_empty_items
from typing import List

logger = Logger('CPP2IL')
WINDOWS_LINK = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-Netframework472-Windows.zip"
LINUX_LINK = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-net7-linux-x64.zip"

def run_cpp2il(state: dict):
	system_name = os.name

	# base state
	ensure_downloaded()
	path = "resources/Cpp2IL" if system_name == "posix" else "resources/cpp2il/Cpp2IL.exe"
	processors = ["attributeanalyzer", "attributeinjector", "callanalyzer", "nativemethoddetector"]
	args = [
		"--verbose",
		"--use-processor", ','.join(processors),
		"--wasm-framework-file", f'{state["output_dir"]}/framework.js',
		"--force-binary-path", f'{state["output_dir"]}/game.wasm',
		"--force-metadata-path", f'{state["output_dir"]}/WebData/Il2CppData/Metadata/global-metadata.dat',
		"--force-unity-version", "2023.2.5",
		"--output-to", f'{state["output_dir"]}/CPP2IL',
	]


	# diffable_cs(path, args)
	offset_dumper(state, path, args)
	# wasm_mappings(state, path, args)

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

		logger.success("Extracted cpp2il!\n")
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

EMPTY_CS_FILE_LENGTH = 2
def offset_dumper(state: dict, path: str, args: List[str]):
	logger.info('Dumping offsets from the Diffable C# files')

	# iterate over all the files in the diffable-cs folder (recursively)
	allOffsets = {}
	for root, _, files in os.walk(f'{state["output_dir"]}/CPP2IL/DiffableCs'):
		# get the current DLL name
		tmproot = root.replace(f'{state["output_dir"]}/CPP2IL/DiffableCs', '')
		tmproot = remove_empty_items(tmproot.split('/'))
		# if the root is empty, skip it
		if not tmproot:
			continue

		# else, continue normally
		tmproot = tmproot[0].strip()
		dllName = tmproot
		if dllName not in allOffsets:
			allOffsets[dllName] = {}

		if dllName == 'output':
			print(root, tmproot)

		for file in files:
			if not file.endswith('.cs'):
				continue

			# dump offsets from the file
			# TODO: figure out how to get offsets from an inherited class
			# TODO: make a merge dictionary function (idk how id deal w double keys but i doubt it'd happen)
			with open(f'{root}/{file}', 'r') as f:
				lines = [str(line).strip() for line in f.readlines() if str(line).strip()]
				if len(lines) == EMPTY_CS_FILE_LENGTH:
					print('empty', lines)
					continue

				className = os.path.splitext(file)[0]
				offsets = process_class(lines)

				# check to see if any keys were even added to the offsets var
				if len(offsets.keys()) == 0:
					continue

				allOffsets[dllName][className] = offsets

	# iterate back over allOffsets and remove empty elements
	for key, value in list(allOffsets.items()):
		if not value:
			allOffsets.pop(key)

	with open(f'{state["output_dir"]}/CPP2IL/offsets.json', 'w') as f:
		f.write(json.dumps(allOffsets, indent=4))

def process_class(lines: List[str], offsets = {}):
	if not offsets:
		offsets = {}

	for line in lines:
		# we only want to check for offsets, not methods or anything
		if '//Field offset: ' not in line:
			continue

		# split line based on spaces and remove unnecessary keywords
		spaceSplit = line.split(' ')
		for i in range(len(spaceSplit)):
			if not len(spaceSplit):
				break

			if spaceSplit[0] in ['public', 'private', 'protected', 'static', 'readonly', 'internal']:
				spaceSplit.pop(0)

		# fieldType = spaceSplit[0]
		fieldName = spaceSplit[1].split(';')[0]
		fieldOffset = spaceSplit[-1] if '0x' in spaceSplit[-1] else '0'
		offsets[fieldName] = int(fieldOffset, 16)

	return offsets


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
