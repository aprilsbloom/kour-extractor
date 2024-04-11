import requests
import re
import os
from logger import Logger
from argparse import ArgumentParser

logger = Logger()
BASE_DOMAIN = 'https://kour.io'
FRAMEWORK_REGEX = r'\"/[a-zA-Z0-9]+.js.br\"'
DATA_REGEX = r'\"/[a-zA-Z0-9]+.data.br\"'
WASM_REGEX = r'\"/[a-zA-Z0-9]+.wasm.br\"'

def remove_wrapped_quotes(string):
	if string[0] == '"':
		string = string[1:]

	if string[-1] == '"':
		string = string[:-1]

	return string

def fetch_kour_files(has_framework = False, has_data_file = False, has_wasm = False):
	r = requests.get(BASE_DOMAIN)

	logger.info("Fetching: Build URL")
	build_url = re.findall(r'var buildUrl = isMobile \? \"[a-zA-Z0-9\/]+\" : \"[a-zA-Z0-9]+\"', r.text)[0]
	build_url = remove_wrapped_quotes(build_url.split('" : ')[1])
	logger.success(f'Build URL: {build_url}')

	if not has_framework:
		logger.
		framework_path = re.findall(FRAMEWORK_REGEX, r.text)[0]
		framework_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(framework_path)
		print(framework_path)

	if not has_data_file:
		data_path = re.findall(DATA_REGEX, r.text)[0]
		data_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(data_path)
		print(data_path)

	if not has_wasm:

		wasm_path = re.findall(WASM_REGEX, r.text)[0]
		wasm_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(wasm_path)
		print(wasm_path)

def main():
	parser = ArgumentParser(description="A simple program")

	parser.add_argument('--framework_path')
	parser.add_argument('--data_path')
	parser.add_argument('--wasm_path')

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

	# fetch only the needed values
	fetch_kour_files(has_framework=has_framework, has_data_file=has_data_file, has_wasm=has_wasm)

if __name__ == "__main__":
	main()