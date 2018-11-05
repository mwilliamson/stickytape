import argparse
import sys
import subprocess

import stickytape

def main():
    args = _parse_args()
    output_file = _open_output(args)
    output = stickytape.script(
        args.script, args.add_python_path, args.python_binary)
    output_file.write(output)

def _open_output(args):
    if args.output_file is None:
        return sys.stdout
    else:
        return open(args.output_file, "w")

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("--add-python-path", action="append", default=[])
    parser.add_argument("--python-binary")
    parser.add_argument("--output-file")
    return parser.parse_args()

if __name__ == "__main__":
    main()

