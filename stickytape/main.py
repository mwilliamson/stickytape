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
        add_resources_files=args.add_resources_file,
        add_resources_modules=args.add_resources_module,
        python_binary=args.python_binary,
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
    parser.add_argument("--add-resources-module", action="append", default=[])
    parser.add_argument("--add-resources-file", action="append", nargs=2, default=[])
    parser.add_argument("--python-binary")
    parser.add_argument("--output-file")
    return parser.parse_args()

if __name__ == "__main__":
    main()

