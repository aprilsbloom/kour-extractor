import requests
import re
import os
from logger import Logger
from argparse import ArgumentParser
from uwdtool import UWDTool
from modules import run_cpp2il, run_wasmtoolkit
from utils import remove_wrapped_quotes, random_string

logger = Logger()
state = {"version": "", "output_dir": ""}

BASE_DOMAIN = "https://kour.io"
VERSION_REGEX = r"productVersion: \"[0-9\.]+\""
BUILD_REGEX = r"var buildUrl = isMobile \? \"[a-zA-Z0-9\/]+\" : \"[a-zA-Z0-9]+\""
FRAMEWORK_REGEX = r"\"\/[a-zA-Z0-9]+.js.br\""
DATA_REGEX = r"\"\/[a-zA-Z0-9]+\.data\.br\""
WASM_REGEX = r"\"\/[a-zA-Z0-9]+.wasm.br\""

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

	# this may be redundant since it's in the folder name lol, but ur call to whoever is reading this
	with open(f'{state["output_dir"]}/version.txt', "w") as f:
		f.write(version)

	with open(f'{state["output_dir"]}/index.html', "w", encoding='utf8') as f:
		f.write(r.text) # they have this weird double newline shit, you can just call .replace('\r', '').replace('\n\n', '\n') at the end of this and it fixes it


	if not has_framework:
		logger.info("Fetching: Framework Path")
		framework_path = re.findall(FRAMEWORK_REGEX, r.text)[0]
		framework_path = (BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(framework_path))
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
		with open(f'{state["output_dir"]}/web.data', "wb") as f:
			f.write(data_res.content)

		# with open(f'{state["output_dir"]}/web.data.sha256', 'w') as f:
		# 	f.write(hash_file(data_res.content))

	if not has_wasm:
		logger.info("Fetching: Web Assembly path")
		wasm_path = re.findall(WASM_REGEX, r.text)[0]
		wasm_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(wasm_path)
		logger.success(f"Fetched: Web Assembly path ({wasm_path})")

		logger.info("Fetching: Web Assembly file")
		wasm_res = requests.get(wasm_path)
		logger.success("Fetched: Web Assembly file, writing...\n")
		with open(f'{state["output_dir"]}/game.wasm', "wb") as f:
			f.write(wasm_res.content)

		# with open(f'{state["output_dir"]}/game.wasm.sha256', 'w') as f:
		# 	f.write(hash_file(wasm_res.content))


def extract_webdata(data_path):
	logger.info("Unpacking Unity WebData file")

	output_path = f'{state["output_dir"]}/WebData'
	os.makedirs(output_path, exist_ok=True)

	unpacker = UWDTool.UnPacker()
	unpacker.unpack(data_path, output_path)  # unpacking

	logger.success("Unpacked Unity WebData file\n")

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

	# fetch needed files
	uid = random_string()
	state['output_dir'] = 'output/v2.41 (YUVC0)'
	# fetch_kour_files(uid, has_framework=has_framework, has_data_file=has_data_file, has_wasm=has_wasm)
	logger.success(f'Files saved to: {state["output_dir"]}\n')

	# extract data we want
	# extract_webdata(f'{state["output_dir"]}/web.data')
	run_cpp2il(state)
	# run_wasmtoolkit(state)

if __name__ == "__main__":
	main()
