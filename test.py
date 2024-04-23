import tarfile
import os
import shutil
import requests

# fetch latest release
r = requests.get('https://api.github.com/repos/WebAssembly/wabt/releases/latest')
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
