import os
import os.path
import tempfile
import contextlib
import platform
import re
import subprocess
import shutil
import sys

from nose.tools import istest, nottest, assert_equal
import spur

import stickytape
from test_scripts import root as test_script_root

@istest
def single_file_script_still_works():
    test_script_output(
        script_path="single_file/hello",
        expected_output=b"Hello\n"
    )

@istest
def stdlib_imports_are_not_modified():
    test_script_output(
        script_path="single_file_using_stdlib/hello",
        expected_output=b"f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0\n"
    )

@istest
def stdlib_module_in_package_is_not_generated():
    test_script_output(
        script_path="script_using_stdlib_module_in_package/hello",
        expected_output=b"xml.etree.ElementTree\nHello\n",
        expected_modules=["greeting"],
        python_binary=sys.executable,
    )

@istest
def script_that_imports_local_module_is_converted_to_single_file():
    test_script_output(
        script_path="script_with_single_local_import/hello",
        expected_output=b"Hello\n"
    )

@istest
def script_that_imports_local_package_is_converted_to_single_file():
    test_script_output(
        script_path="script_with_single_local_import_of_package/hello",
        expected_output=b"Hello\n"
    )

@istest
def can_import_module_from_package():
    test_script_output(
        script_path="script_using_module_in_package/hello",
        expected_output=b"Hello\n"
    )

@istest
def can_import_value_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_with_single_local_from_import/hello",
        expected_output=b"Hello\n"
    )

@istest
def can_import_multiple_values_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_multiple_values/hello",
        expected_output=b"Hello\n"
    )

@istest
def can_import_module_from_package_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_module/hello",
        expected_output=b"Hello\n"
    )

@istest
def can_import_multiple_modules_from_module_using_from_import_syntax():
    test_script_output(
        script_path="script_using_from_to_import_multiple_modules/hello",
        expected_output=b"Hello\n"
    )

@istest
def imported_modules_are_transformed():
    test_script_output(
        script_path="imports_in_imported_modules/hello",
        expected_output=b"Hello\n"
    )

@istest
def circular_references_dont_cause_stack_overflow():
    test_script_output(
        script_path="circular_reference/hello",
        expected_output=b"Hello\n"
    )

@istest
def explicit_relative_imports_with_single_dot_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import_single_dot/hello",
        expected_output=b"Hello\n"
    )

@istest
def explicit_relative_imports_with_single_dot_in_package_init_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import_single_dot_in_init/hello",
        expected_output=b"Hello\n"
    )

@istest
def explicit_relative_imports_from_parent_package_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import_from_parent_package/hello",
        expected_output=b"Hello\n"
    )

@istest
def explicit_relative_imports_with_module_name_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import/hello",
        expected_output=b"Hello\n"
    )

@istest
def explicit_relative_imports_with_module_name_in_package_init_are_resolved_correctly():
    test_script_output(
        script_path="explicit_relative_import_in_init/hello",
        expected_output=b"Hello\n"
    )


@istest
def package_init_can_be_used_even_if_not_imported_explicitly():
    test_script_output(
        script_path="implicit_init_import/hello",
        expected_output=b"Hello\n"
    )


@istest
def value_import_is_detected_when_import_is_renamed():
    test_script_output(
        script_path="import_from_as_value/hello",
        expected_output=b"Hello\n"
    )


@istest
def module_import_is_detected_when_import_is_renamed():
    test_script_output(
        script_path="import_from_as_module/hello",
        expected_output=b"Hello\n"
    )


@istest
def can_explicitly_set_python_interpreter():
    with _temporary_directory() as temp_path:
        venv_path = os.path.join(temp_path, "venv")
        _shell.run(["virtualenv", venv_path])
        site_packages_path = _find_site_packages(venv_path)
        path_path = os.path.join(site_packages_path, "greetings.pth")
        with open(path_path, "w") as path_file:
            path_file.write(find_script("python_path_from_binary/packages\n"))

        test_script_output(
            script_path="python_path_from_binary/hello",
            expected_output=b"Hello\n",
            python_binary=_venv_python_binary_path(venv_path),
        )


@istest
def python_environment_variables_are_ignored_when_explicitly_setting_python_interpreter():
    with _temporary_directory() as temp_path:
        venv_path = os.path.join(temp_path, "venv")
        _shell.run(["virtualenv", venv_path])
        site_packages_path = _find_site_packages(venv_path)
        path_path = os.path.join(site_packages_path, "greetings.pth")

        bad_python_path = os.path.join(venv_path, "pythonpath")
        bad_import_path = os.path.join(bad_python_path, "greetings/greeting.py")
        os.makedirs(os.path.dirname(bad_import_path))
        with open(bad_import_path, "w") as bad_import_path:
            pass

        with open(path_path, "w") as path_file:
            path_file.write(find_script("python_path_from_binary/packages\n"))

        original_python_path = os.environ.get("PYTHONPATH")
        os.environ["PYTHONPATH"] = bad_python_path
        try:

            test_script_output(
                script_path="python_path_from_binary/hello",
                expected_output=b"Hello\n",
                python_binary=_venv_python_binary_path(venv_path),
            )
        finally:
            if original_python_path is None:
                del os.environ["PYTHONPATH"]
            else:
                os.environ["PYTHONPATH"] = original_python_path


@istest
def can_explicitly_copy_shebang():
    test_script_output(
        script_path="script_with_special_shebang/hello",
        expected_output=b"1\n",
        copy_shebang=True,
    )


@istest
def modules_with_triple_quotes_can_be_bundled():
    test_script_output(
        script_path="module_with_triple_quotes/hello",
        expected_output=b"Hello\n'''\n\"\"\"\n"
    )


@istest
def additional_python_modules_can_be_explicitly_included():
    test_script_output(
        script_path="script_with_dynamic_import/hello",
        expected_output=b"Hello\n",
        add_python_modules=("greeting", ),
    )


def _find_site_packages(root):
    paths = []

    for dir_path, dir_names, file_names in os.walk(root):
        for dir_name in dir_names:
            path = os.path.join(dir_path, dir_name)
            if dir_name == "site-packages" and os.listdir(path):
                paths.append(path)

    if len(paths) == 1:
        return paths[0]
    else:
        raise ValueError("Multiple site-packages found: {}".format(paths))



_shell = spur.LocalShell()


@nottest
def test_script_output(script_path, expected_output, expected_modules=None, **kwargs):
    result = stickytape.script(find_script(script_path), **kwargs)

    if expected_modules is not None:
        actual_modules = set(re.findall(r"__stickytape_write_module\('([^']*)\.py'", result))
        assert_equal(set(expected_modules), actual_modules)

    with _temporary_script(result) as script_file_path:
        try:
            if _is_windows():
                command = ["py", script_file_path]
            else:
                command = [script_file_path]

            output = _shell.run(command).output.replace(b"\r\n", b"\n")
        except:
            for index, line in enumerate(result.splitlines()):
                print((index + 1), line)
            raise
        assert_equal(expected_output, output)


def find_script(path):
    return os.path.join(test_script_root, path)

@contextlib.contextmanager
def _temporary_script(contents):
    with _temporary_directory() as dir_path:
        path = os.path.join(dir_path, "script")
        with open(path, "w") as script_file:
            script_file.write(contents)

        _shell.run(["chmod", "+x", path])
        yield path


@contextlib.contextmanager
def _temporary_directory():
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)


def _venv_python_binary_path(venv_path):
    if _is_windows():
        bin_directory = "Scripts"
    else:
        bin_directory = "bin"

    return os.path.join(venv_path, bin_directory, "python")


def _is_windows():
    return platform.system() == "Windows"
