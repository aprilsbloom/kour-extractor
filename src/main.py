from modules import CPP2IL, WABT

def main():
	cpp2il = CPP2IL()
	cpp2il.diffable_cs()
	cpp2il.wasm_mappings()

	wabt = WABT()
	wabt.to_wat()
	wabt.decompile()