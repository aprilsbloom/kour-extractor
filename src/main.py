import requests
import re
import os
import random
import string
import hashlib
import zipfile
import subprocess
from logger import Logger
from argparse import ArgumentParser
from uwdtool import UWDTool

logger = Logger()
state = {"version": "", "output_dir": ""}

BASE_DOMAIN = "https://kour.io"
VERSION_REGEX = r"productVersion: \"[0-9\.]+\""
BUILD_REGEX = r"var buildUrl = isMobile \? \"[a-zA-Z0-9\/]+\" : \"[a-zA-Z0-9]+\""
FRAMEWORK_REGEX = r"\"\/[a-zA-Z0-9]+.js.br\""
DATA_REGEX = r"\"\/[a-zA-Z0-9]+\.data\.br\""
WASM_REGEX = r"\"\/[a-zA-Z0-9]+.wasm.br\""
CHAR_LIST = string.ascii_letters + string.digits


def hash_file(bytes):
	return hashlib.sha256(bytes).hexdigest()


def random_string(length=8):
	return "".join([random.choice(CHAR_LIST) for i in range(length)])


def remove_wrapped_quotes(str):
	if str[0] == '"':
		str = str[1:]

	if str[-1] == '"':
		str = str[:-1]

	return str


def fetch_kour_files(uid, has_framework=False, has_data_file=False, has_wasm=False):
	r = requests.get(BASE_DOMAIN)

	logger.info("Fetching: Game version")
	version = remove_wrapped_quotes(re.findall(VERSION_REGEX, r.text)[0]).split('"')[1]
	state["version"] = version
	logger.success(f"Fetched: Game version (v{version})\n")

	logger.info("Fetching: Build URL")
	build_url = re.findall(BUILD_REGEX, r.text)[0]
	build_url = remove_wrapped_quotes(build_url.split('" : ')[1])
	logger.success(f"Fetched: Build URL (https://kour.io/{build_url})\n")

	state["output_dir"] = f"output/v{version} ({uid})"
	os.makedirs(state["output_dir"], exist_ok=True)

	if not has_framework:
		logger.info("Fetching: Framework Path")
		framework_path = re.findall(FRAMEWORK_REGEX, r.text)[0]
		framework_path = (
			BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(framework_path)
		)
		logger.success(f"Fetched: Framework Path ({framework_path})")

		logger.info("Fetching: Actual framework file")
		framework_res = requests.get(framework_path)
		logger.success("Fetched: Actual framework file, writing...\n")
		with open(f'{state["output_dir"]}/framework.js', "wb") as f:
			f.write(framework_res.content)

		# with open(f'{state["output_dir"]}/framework.js.sha256', 'w') as f:
		# 	f.write(hash_file(framework_res.content))

	if not has_data_file:
		logger.info("Fetching: Unity WebData path")
		data_path = re.findall(DATA_REGEX, r.text)[0]
		data_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(data_path)
		logger.success(f"Fetched: Unity WebData path ({data_path})")

		logger.info("Fetching: Unity WebData file")
		data_res = requests.get(data_path)
		logger.success("Fetched: Unity WebData file, writing...\n")
		with open(f'{state["output_dir"]}/kour.data', "wb") as f:
			f.write(data_res.content)

		# with open(f'{state["output_dir"]}/kour.data.sha256', 'w') as f:
		# 	f.write(hash_file(data_res.content))

	if not has_wasm:
		logger.info("Fetching: Web Assembly path")
		wasm_path = re.findall(WASM_REGEX, r.text)[0]
		wasm_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(wasm_path)
		logger.success(f"Fetched: Web Assembly path ({wasm_path})")

		logger.info("Fetching: Web Assembly file")
		wasm_res = requests.get(wasm_path)
		logger.success("Fetched: Web Assembly file, writing...\n")
		with open(f'{state["output_dir"]}/kour.wasm', "wb") as f:
			f.write(wasm_res.content)

		# with open(f'{state["output_dir"]}/kour.wasm.sha256', 'w') as f:
		# 	f.write(hash_file(wasm_res.content))


def extract_webdata(data_path):
	logger.info("Unpacking Unity WebData file")

	output_path = f'{state["output_dir"]}/WebData'
	os.makedirs(output_path, exist_ok=True)

	unpacker = UWDTool.UnPacker()
	unpacker.unpack(data_path, output_path)  # unpacking

	logger.success("Unpacked Unity WebData file")


def run_cpp2il():
	system_name = os.name

	# setup resources folder (just incase)
	os.makedirs("resources", exist_ok=True)

	# download cpp2il if it hasn't been downloaded already
	if (system_name == "nt" and not os.path.exists("resources/cpp2il/Cpp2IL.exe")) or (system_name == "posix" and not os.path.exists("resources/Cpp2IL")):
		logger.info("Downloading cpp2il!")

		# fetch the latest cpp2il release (nightly build)
		if system_name == "nt":
			r = requests.get("https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-Netframework472-Windows.zip")
		elif system_name == "posix":
			r = requests.get("https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-net7-linux-x64.zip")
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

	# cpp2il base state
	cpp2il_path = "resources/Cpp2IL" if system_name == "posix" else "resources/cpp2il/Cpp2IL.exe"
	cpp2il_args = [
		"--verbose",
		"--use-processor", "attributeanalyzer,attributeinjector,callanalyzer,nativemethoddetector",
		"--wasm-framework-file", f'{state["output_dir"]}/framework.js',
		"--force-binary-path", f'{state["output_dir"]}/kour.wasm',
		"--force-metadata-path", f'{state["output_dir"]}/WebData/Il2CppData/Metadata/global-metadata.dat',
		"--force-unity-version", "2023.2.5",
		"--output-to", f'{state["output_dir"]}/CPP2IL',
	]

	# diffable cs
	subprocess.run([
		cpp2il_path,
		*cpp2il_args,
		'--output-as', 'diffable-cs'
	])

	# wasm mappings
	subprocess.run([
		cpp2il_path,
		*cpp2il_args,
		'--output-as', 'wasmmappings'
	])

	# isil
	subprocess.run([
		cpp2il_path,
		*cpp2il_args,
		'--output-as', 'isil'
	])



def main():
	parser = ArgumentParser(description="A simple program")

	parser.add_argument("--framework_path")
	parser.add_argument("--data_path")
	parser.add_argument("--wasm_path")

	args = parser.parse_args()

	# determine if user has passed in paths for the respective files
	has_framework = False
	has_data_file = False
	has_wasm = False

	if args.framework_path and os.path.exists(args.framework_path):
		has_framework = True

	if args.data_path and os.path.exists(args.data_path):
		has_data_file = True

	if args.wasm_path and os.path.exists(args.wasm_path):
		has_wasm = True

	state["output_dir"] = "output/good"
	run_cpp2il()
	# uid = random_string()
	# fetch_kour_files(uid, has_framework=has_framework, has_data_file=has_data_file, has_wasm=has_wasm)
	# logger.success(f'Files saved to: {state["output_dir"]}\n')

	# extract_webdata(f'{state["output_dir"]}/kour.data')


if __name__ == "__main__":
	main()
