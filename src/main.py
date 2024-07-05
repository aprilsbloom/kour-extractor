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
VERSION_REGEX = r"productVersion:(?: |)\"([0-9.]+)"
BUILD_REGEX = r"buildUrl(?: |)=(?: |)(?:[a-zA-Z +\?]+)\"(?:[a-zA-Z:\/\-\.\ ]+)\"(?: |):(?: |)\"([a-zA-Z:\/\-\.\ ]+)"
FRAMEWORK_REGEX = r"frameworkUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
DATA_REGEX = r"dataUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""
WASM_REGEX = r"codeUrl:(?: |)buildUrl(?: |)\+(?: |)\"([a-zA-Z0-9.\/]+)\""

def fetch_kour_files(uid):
	r = requests.get(BASE_DOMAIN)

	logger.info("Fetching: Game version")
	version = re.findall(VERSION_REGEX, r.text)[0]
	state["version"] = version
	logger.success(f"Fetched: Game version (v{version})\n")

	logger.info("Fetching: Build URL")
	build_url = re.findall(BUILD_REGEX, r.text)[0]
	logger.success("Fetched: Build URL (build_url)\n")

	state["output_dir"] = f"output/v{version} ({uid})"
	os.makedirs(state["output_dir"], exist_ok=True)

	# this may be redundant since it's in the folder name lol, but ur call to whoever is reading this
	with open(f'{state["output_dir"]}/version.txt', "w") as f:
		f.write(version)

	with open(f'{state["output_dir"]}/index.html', "w", encoding='utf8') as f:
		f.write(r.text) # they have this weird double newline shit, you can just call .replace('\r', '').replace('\n\n', '\n') at the end of this and it fixes it


	# framework js file
	logger.info("Fetching: Framework Path")
	framework_path = build_url + re.findall(FRAMEWORK_REGEX, r.text)[0]
	logger.success(f"Fetched: Framework Path ({framework_path})")

	logger.info("Fetching: Actual framework file")
	framework_res = requests.get(framework_path)
	logger.success("Fetched: Actual framework file, writing...\n")
	with open(f'{state["output_dir"]}/framework.js', "wb") as f:
		f.write(framework_res.content)


	# webdata file
	logger.info("Fetching: Unity WebData path")
	data_path = build_url + re.findall(DATA_REGEX, r.text)[0]
	logger.success(f"Fetched: Unity WebData path ({data_path})")

	logger.info("Fetching: Unity WebData file")
	data_res = requests.get(data_path)
	logger.success("Fetched: Unity WebData file, writing...\n")
	with open(f'{state["output_dir"]}/web.data', "wb") as f:
		f.write(data_res.content)


	# game wasm
	logger.info("Fetching: Web Assembly path")
	wasm_path = build_url + re.findall(WASM_REGEX, r.text)[0]
	logger.success(f"Fetched: Web Assembly path ({wasm_path})")

	logger.info("Fetching: Web Assembly file")
	wasm_res = requests.get(wasm_path)
	logger.success("Fetched: Web Assembly file, writing...\n")
	with open(f'{state["output_dir"]}/game.wasm', "wb") as f:
		f.write(wasm_res.content)


def extract_webdata(data_path):
	logger.info("Unpacking Unity WebData file")

	output_path = f'{state["output_dir"]}/WebData'
	os.makedirs(output_path, exist_ok=True)

	unpacker = UWDTool.UnPacker()
	unpacker.unpack(data_path, output_path)  # unpacking

	logger.success("Unpacked Unity WebData file\n")

def main():
	# parser = ArgumentParser(description="A simple program")
	# args = parser.parse_args()

	# fetch needed files
	uid = random_string()
	fetch_kour_files(uid)
	logger.success(f'Files saved to: {state["output_dir"]}\n')

	# extract data we want
	extract_webdata(f'{state["output_dir"]}/web.data')
	# run_cpp2il(state)
	run_wasmtoolkit(state)

if __name__ == "__main__":
	main()
