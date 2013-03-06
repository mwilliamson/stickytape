import os
import os.path
import tempfile
import contextlib
import subprocess
import shutil

from nose.tools import istest, assert_equal

import stickytape
from test_scripts import root as test_script_root

@istest
def single_file_script_still_works():
    test_script_output(
        script_path="single_file/hello",
        expected_output="Hello\n"
    )

@istest
def stdlib_imports_are_not_modified():
    test_script_output(
        script_path="single_file_using_stdlib/hello",
        expected_output="f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0\n"
    )
        
@istest
def script_that_imports_local_module_is_converted_to_single_file():
    test_script_output(
        script_path="script_with_single_local_import/hello",
        expected_output="Hello\n"
    )
        
@istest
def script_that_imports_local_package_is_converted_to_single_file():
    test_script_output(
        script_path="script_with_single_local_import_of_package/hello",
        expected_output="Hello\n"
    )
        
@istest
def can_import_module_from_package():
    test_script_output(
        script_path="script_using_module_in_package/hello",
        expected_output="Hello\n"
    )
        
@istest
def can_import_value_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_with_single_local_from_import/hello",
        expected_output="Hello\n"
    )
        
@istest
def can_import_multiple_values_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_multiple_values/hello",
        expected_output="Hello\n"
    )
        
@istest
def can_import_module_from_package_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_module/hello",
        expected_output="Hello\n"
    )
        
@istest
def can_import_multiple_modules_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_multiple_modules/hello",
        expected_output="Hello\n"
    )
    
@istest
def imported_modules_are_transformed():
    test_script_output(
        script_path="imports_in_imported_modules/hello",
        expected_output="Hello\n"
    )
    
@istest
def circular_references_dont_cause_stack_overflow():
    test_script_output(
        script_path="circular_reference/hello",
        expected_output="Hello\n"
    )
    
@istest
def implictly_relative_imports_are_resolved_correctly():
    test_script_output(
        script_path="implicit_relative_import/hello",
        expected_output="Hello\n"
    )
    
@istest
def explicit_relative_imports_with_single_dot_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import_single_dot/hello",
        expected_output="Hello\n"
    )
    
@istest
def explicit_relative_imports_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import/hello",
        expected_output="Hello\n"
    )


@istest
def package_init_can_be_used_even_if_not_imported_explicitly():
    test_script_output(
        script_path="implicit_init_import/hello",
        expected_output="Hello\n"
    )
    
    
def test_script_output(script_path, expected_output):
    result = stickytape.script(find_script(script_path))
    with _temporary_script(result) as script_file_path:
        output = subprocess.check_output([script_file_path])
        assert_equal(expected_output, output)
    

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
