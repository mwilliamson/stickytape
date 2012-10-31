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
    result = stickytape.stick(find_script("single_file/hello"))
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
