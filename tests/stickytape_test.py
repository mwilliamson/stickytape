import os
import os.path
import tempfile
import contextlib
import subprocess
import shutil

from nose.tools import istest, assert_equal

import stickytape
from .test_scripts import root as test_script_root


@istest
def single_file_script_still_works():
    result = stickytape.script(find_script("single_file/hello"))
    with _temporary_script(result) as script_file_path:
        output = subprocess.check_output([script_file_path])
        assert_equal("Hello\n", output)

@istest
def stdlib_imports_are_not_modified():
    result = stickytape.script(find_script("single_file_using_stdlib/hello"))
    with _temporary_script(result) as script_file_path:
        output = subprocess.check_output([script_file_path])
        assert_equal("f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0\n", output)
        
@istest
def script_that_imports_local_module_is_converted_to_single_file():
    result = stickytape.script(find_script("script_with_single_local_import/hello"))
    with _temporary_script(result) as script_file_path:
        output = subprocess.check_output([script_file_path])
        assert_equal("Hello\n", output)

def find_script(path):
    return os.path.join(test_script_root, path)

@contextlib.contextmanager
def _temporary_script(contents):
    dir_path = tempfile.mkdtemp()
    try:
        path = os.path.join(dir_path, "script")
        with open(path, "w") as script_file:
            script_file.write(contents)
            
        subprocess.check_call(["chmod", "+x", path])
        yield path
    finally:
        shutil.rmtree(dir_path)
