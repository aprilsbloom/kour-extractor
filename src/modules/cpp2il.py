from typing import Final

from logger import Logger

logger = Logger("CPP2IL")
class CPP2IL():
	WINDOWS_LINK: Final[str] = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-Netframework472-Windows.zip"
	LINUX_LINK: Final[str] = "https://nightly.link/SamboyCoding/Cpp2IL/workflows/dotnet-core/development/Cpp2IL-net7-linux-x64.zip"

	def __init__(self) -> None:
		self.path = ''
		self.processors = ["attributeanalyzer", "attributeinjector", "callanalyzer", "nativemethoddetector"]
		self.args = [
			"--verbose",
			"--use-processor", ','.join(self.processors),
			"--wasm-framework-file", f'{self.path}/framework.js',
			"--force-binary-path", f'{self.path}/game.wasm',
			"--force-metadata-path", f'{self.path}/WebData/Il2CppData/Metadata/global-metadata.dat',
			"--force-unity-version", "2022.2.5",
			"--output-to", f'{self.path}/CPP2IL',
		]

		self.ensure_downloaded()

	def ensure_downloaded(self):
		pass

	def diffable_cs(self):
		pass

	def wasm_mappings(self):
		pass

