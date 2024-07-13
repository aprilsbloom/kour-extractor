# Kour.io extractor
This is a tool to automatically extract the relevant files needed to reverse [Kour.io](https://kour.io/), a browser game made in Unity.

## Installation
```bash
git clone https://github.com/paintingofblue/kour-extractor
cd kour-extractor
pip install -r requirements.txt
python src/main.py
```

## Args
- `-w, --wabt-path`: The path to the [WABT](https://github.com/WebAssembly/wabt) folder
- `-c, --cpp2il-path`: The path to the [CPP2IL](https://github.com/SamboyCoding/Cpp2IL) folder
- `--silent`: Prevents commands from outputting to console