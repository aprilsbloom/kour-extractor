import os
import re
import shutil
import subprocess
import tarfile
import requests
from typing import Final

from utils import API
from logger import Logger

logger = Logger("WABT")
class WABT():
	WABT_REPO: Final[str] = 'https://api.github.com/repos/WebAssembly/wabt/releases/latest'
	WABT_VERSION_REGEX: Final[str] = r'download\/([0-9.]+)'

	def __init__(self) -> None:
		self.args = [
			f'{API.path}/game.wasm',
			'--enable-all',
		]

		self.__ensure_downloaded()

	def __ensure_downloaded(self):
		# setup wabt folder (just incase)
		os.makedirs(API.wabt_path, exist_ok=True)

		# download wabt if it hasn't been downloaded already
		if (
			(os.name == "nt" and os.path.exists(f"{API.wabt_path}/wasm2wat.exe")) or
			(os.name == "posix" and os.path.exists(f'{API.wabt_path}/wasm2wat'))
		):
			logger.info("Found WABT path.")
			return

		logger.info("Downloading WABT")

		r = requests.get(self.WABT_REPO)
		if r.status_code != 200:
			logger.error("Failed to get WABT's latest release.")
			return

		# get the latest version of WABT for the current platform
		sys_name = 'windows' if os.name == 'nt' else 'ubuntu' if os.name == 'posix' else 'macos'
		for asset in r.json().get('assets', []):
			# If the asset isn't for the current platform
			if sys_name not in asset['name']:
				continue

			# If the asset is hashed
			if '.sha256' in asset['name']:
				continue

			# Download the release
			asset_url = asset.get('browser_download_url')
			version = re.findall(self.WABT_VERSION_REGEX, asset_url)[0]
			asset_res = requests.get(asset_url)
			with open('wabt.tar.gz', 'wb') as f:
				f.write(asset_res.content)

			# extract the tar archive
			try:
				with tarfile.open('wabt.tar.gz', 'r:gz') as f:
					f.extractall(API.wabt_path)
			except tarfile.ReadError: # this just happens??? idfk why but it still extracts perfectly fine lol its so weird
				pass

			# move the bin folder to the root directory
			for file in os.listdir(f'{API.wabt_path}/wabt-{version}/bin'):
				shutil.move(f'{API.wabt_path}/wabt-{version}/bin/{file}', API.wabt_path)

			# remove redundant files
			shutil.rmtree(f'{API.wabt_path}/wabt-{version}')
			os.remove('wabt.tar.gz')

			# make all files in the wabt directory executable when on linux
			if sys_name != 'windows':
				os.system('chmod +x {API.wabt_path}/*')

	def to_wat(self):
		logger.info('Running wasm2wat (this may take a while)')

		path = f'{API.wabt_path}/wasm2wat{".exe" if os.name == "nt" else ""}'
		output = subprocess.run([
			path,
			*self.args,
			'--output', f'{API.path}/game.wat'
		], capture_output=API.silent)

		# error handling
		if output.returncode == 0:
			logger.success('game.wat generated!')
		else:
			logger.error('An error likely occurred during the generation of game.wat.')
			if (output.stderr):
				print(output.stderr.decode('utf-8').splitlines()[-15:])

	def decompile(self):
		logger.info('Running wasm-decompile (this may take a while)')

		path = f'{API.wabt_path}/wasm-decompile{".exe" if os.name == "nt" else ""}'
		output = subprocess.run([
			path,
			*self.args,
			'--output', f'{API.path}/game.wasm.dcmp'
		])

		# if the return code is not 0, an error likely occurred
		if output.returncode != 0:
			logger.error('An error likely occurred during WASM decompilation.')
			print(output.stderr.decode('utf-8').splitlines()[-15:])
		else:
			logger.success('WASM decompiled!')