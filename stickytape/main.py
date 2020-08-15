import argparse
import sys

import stickytape

def main():
    args = _parse_args()
    output_file = _open_output(args)
    output = stickytape.script(
        args.script,
        add_python_modules=args.add_python_module,
        add_python_paths=args.add_python_path,
        python_binary=args.python_binary,
        copy_shebang=args.copy_shebang
    )
    output_file.write(output)

def _open_output(args):
    if args.output_file is None:
        return sys.stdout
    else:
        return open(args.output_file, "w")

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("--add-python-module", action="append", default=[])
    parser.add_argument("--add-python-path", action="append", default=[])
    parser.add_argument("--python-binary")
    parser.add_argument("--output-file")
    parser.add_argument("--copy-shebang", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    main()

