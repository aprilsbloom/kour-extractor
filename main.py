import requests
import re
import os
import random
import string
from logger import Logger
from argparse import ArgumentParser

logger = Logger()
BASE_DOMAIN = 'https://kour.io'
VERSION_REGEX = r'productVersion: \"[0-9\.]+\"'
BUILD_REGEX = r'var buildUrl = isMobile \? \"[a-zA-Z0-9\/]+\" : \"[a-zA-Z0-9]+\"'
FRAMEWORK_REGEX = r'\"\/[a-zA-Z0-9]+.js.br\"'
DATA_REGEX = r'\"\/[a-zA-Z0-9]+\.data\.br\"'
WASM_REGEX = r'\"\/[a-zA-Z0-9]+.wasm.br\"'

char_list = string.ascii_letters + string.digits
def random_string(length = 8):
	return ''.join([random.choice(char_list) for i in range(length)])

def remove_wrapped_quotes(str):
	if str[0] == '"':
		str = str[1:]

	if str[-1] == '"':
		str = str[:-1]

	return str

def fetch_kour_files(has_framework = False, has_data_file = False, has_wasm = False):
	r = requests.get(BASE_DOMAIN)

	logger.info('Fetching: Game version')
	version = remove_wrapped_quotes(re.findall(VERSION_REGEX, r.text)[0]).split('"')[1]
	logger.success('Fetched: Game version')
	logger.info(f'Version: {version}\n')
	version_uid = random_string()
	version_path = f'output/v{version} ({version_uid})'
	os.makedirs(version_path)


	logger.info("Fetching: Build URL")
	build_url = re.findall(BUILD_REGEX, r.text)[0]
	build_url = remove_wrapped_quotes(build_url.split('" : ')[1])
	logger.success('Fetched: Build URL')
	logger.info(f'Build URL: {build_url}\n')

	if not has_framework:
		logger.info("Fetching: Framework Path")
		framework_path = re.findall(FRAMEWORK_REGEX, r.text)[0]
		framework_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(framework_path)
		logger.success('Fetched: Framework Path')
		logger.info(f'Framework Path: {framework_path}\n')

		framework_res = requests.get(framework_path)
		with open(f'{version_path}/framework.js', 'w', encoding='utf8') as f:
			f.write(framework_res.text)

	if not has_data_file:
		logger.info("Fetching: Unity WebData path")
		data_path = re.findall(DATA_REGEX, r.text)[0]
		data_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(data_path)
		logger.success('Fetched: Unity WebData path')
		logger.info(f'Unity WebData path: {data_path}\n')

		data_res = requests.get(data_path)
		with open(f'{version_path}/kour.data', 'w', encoding='utf8') as f:
			f.write(data_res.text)

	if not has_wasm:
		logger.info("Fetching: Web Assembly path")
		wasm_path = re.findall(WASM_REGEX, r.text)[0]
		wasm_path = BASE_DOMAIN + "/" + build_url + remove_wrapped_quotes(wasm_path)
		logger.success('Fetched: Web Assembly path')
		logger.info(f'Web Assembly path: {wasm_path}\n')

		wasm_res = requests.get(wasm_path)
		with open(f'{version_path}/kour.wasm', 'w', encoding='utf8') as f:
			f.write(wasm_res.text)

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