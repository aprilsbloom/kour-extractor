import os
import random
import string
import argparse

def random_string(length: int) -> str:
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class API:
	uuid: str = random_string(4)
	version: str
	path: str

	cmd_args: argparse.Namespace
	wabt_path: str
	cpp2il_path: str
	silent: bool = False

	@staticmethod
	def parse_cmdline_args():
		parser = argparse.ArgumentParser(description='Kour.io extractor')
		parser.add_argument('-w', '--wabt-path', type=str, help='Path to WABT binaries', default='resources/wabt')
		parser.add_argument('-c', '--cpp2il-path', type=str, help='Path to CPP2IL binaries', default='resources/cpp2il')
		parser.add_argument('-s', '--silent', action=argparse.BooleanOptionalAction, help='Prevents commands from outputting to console', default=False)

		API.cmd_args = parser.parse_args()
		API.wabt_path = API.cmd_args.wabt_path
		API.cpp2il_path = API.cmd_args.cpp2il_path
		API.silent = API.cmd_args.silent

		os.makedirs(API.wabt_path, exist_ok=True)
		os.makedirs(API.cpp2il_path, exist_ok=True)

		# if not os.path.exists(API.wabt_path):
		# 	raise FileNotFoundError(f'WABT binaries not found at {API.wabt_path}')

		# if not os.path.exists(API.cpp2il_path):
		# 	raise FileNotFoundError(f'CPP2IL binaries not found at {API.cpp2il_path}')

	@staticmethod
	def setup_directory():
		API.path = f'output/{API.version} ({API.uuid})'
		os.makedirs(API.path, exist_ok=True)