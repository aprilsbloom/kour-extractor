from utils import API
from modules import Setup, CPP2IL, WABT

def main():
	API.parse_cmdline_args()

	setup = Setup()
	setup.fetch_kour_files()

	cpp2il = CPP2IL()
	cpp2il.diffable_cs()
	cpp2il.wasm_mappings()

	wabt = WABT()
	wabt.to_wat()
	# wabt.decompile()

if __name__ == "__main__":
	main()