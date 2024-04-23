import os
import subprocess
import tarfile
import requests
import shutil
from typing import List
from logger import Logger

logger = Logger('WABT')
WASM_REPO = 'https://api.github.com/repos/WebAssembly/wabt/releases/latest'

def run_wasmtoolkit(state: dict):
	# base state
	ensure_downloaded()
	args = [
		f'{state["output_dir"]}/kour.wasm',
		'--enable-all',
	]

	wasm2wat(state, args)
	wasm_decompile(state, args)


def ensure_downloaded():
	# check to see if wabt exists in the resources folder
	os.makedirs("resources", exist_ok=True)
	if not os.path.exists('resources/wabt'):
		logger.info('Downloading WABT')

		# fetch latest release
		r = requests.get(WASM_REPO)
		assets = r.json().get('assets', [])
		if len(assets) == 0:
			raise Exception("No assets found!")

		# go through each asset and check if it matches the current system
		system_name = 'ubuntu' if os.name == 'posix' else 'windows'
		for asset in assets:
			asset_name = asset.get('name', '')

			# check to see if the asset is for the current system (and isn't a sha256 file)
			if system_name in asset_name and '.sha256' not in asset_name:
				asset_url = asset.get('browser_download_url')
				asset_res = requests.get(asset_url)
				with open('wabt.tar.gz', 'wb') as f:
					f.write(asset_res.content)

				# extract the tar.gz
				try:
					with tarfile.open('wabt.tar.gz', 'r:gz') as f:
						f.extractall('resources/wabt/')
				except tarfile.ReadError: # this just happens??? idfk why but it still extracts perfectly fine lol its so weird
					pass

				# move the bin folder to the root directory & remove redundant files
				shutil.move('resources/wabt/wabt-1.0.34/bin', 'resources/')
				shutil.rmtree('resources/wabt')

				os.rename('resources/bin', 'resources/wabt')
				os.remove('wabt.tar.gz')

				# make all files in the wabt directory executable when on linux
				if os.name == 'posix':
					os.system('chmod +x resources/wabt/*')

		logger.success('WABT downloaded!\n')



# ==== Methods ==== #
def wasm2wat(state: dict, args: List[str]):
	logger.info('Running wasm2wat (this may take a while)')
	path = 'resources/wabt/wasm2wat' if os.name == 'posix' else 'resources/wabt/wasm2wat.exe'
	output = subprocess.run([
		path,
		*args,
		'--output', f'{state["output_dir"]}/kour.wasm.wat'
	], capture_output=True)

	# if the return code is not 0, an error likely occurred
	if output.returncode != 0:
		logger.error('An error likely occurred during the generation of kour.wasm.wat.\n')
		print(output.stderr.decode('utf-8').splitlines()[-15:])
	else:
		logger.success('kour.wasm.wat generated!\n')

def wasm_decompile(state: dict, args: List[str]):
	logger.info('Running wasm-decompile (this may take a while)')
	path = 'resources/wabt/wasm-decompile' if os.name == 'posix' else 'resources/wabt/wasm-decompile.exe'
	output = subprocess.run([
		path,
		*args,
		'--output', f'{state["output_dir"]}/kour.wasm.dcmp'
	])

	# if the return code is not 0, an error likely occurred
	if output.returncode != 0:
		logger.error('An error likely occurred during wasm decompilation.\n')
		print(output.stderr.decode('utf-8').splitlines()[-15:])
	else:
		logger.success('WASM decompiled!\n')