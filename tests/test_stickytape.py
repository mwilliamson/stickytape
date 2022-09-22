import os
import os.path
import sys
import pytest


def test_single_file_script_still_works(chk_script_output):
    chk_script_output(script_path="single_file/hello", expected_output=b"Hello\n")


def test_stdlib_imports_are_not_modified(chk_script_output):
    chk_script_output(
        script_path="single_file_using_stdlib/hello", expected_output=b"f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0\n"
    )


def test_stdlib_module_in_package_is_not_generated(chk_script_output):
    chk_script_output(
        script_path="script_using_stdlib_module_in_package/hello",
        expected_output=b"xml.etree.ElementTree\nHello\n",
        expected_modules=["greeting"],
        python_binary=sys.executable,
    )


def test_script_that_imports_local_module_is_converted_to_single_file(chk_script_output):
    chk_script_output(script_path="script_with_single_local_import/hello", expected_output=b"Hello\n")


def test_script_that_imports_local_package_is_converted_to_single_file(chk_script_output):
    chk_script_output(script_path="script_with_single_local_import_of_package/hello", expected_output=b"Hello\n")


def test_can_import_module_from_package(chk_script_output):
    chk_script_output(script_path="script_using_module_in_package/hello", expected_output=b"Hello\n")


def test_can_import_value_from_module_using_from_import_syntax(chk_script_output):
    chk_script_output(script_path="script_with_single_local_from_import/hello", expected_output=b"Hello\n")


def test_can_import_multiple_values_from_module_using_from_import_syntax(chk_script_output):
    chk_script_output(script_path="script_using_from_to_import_multiple_values/hello", expected_output=b"Hello\n")


def test_can_import_module_from_package_using_from_import_syntax(chk_script_output):
    chk_script_output(script_path="script_using_from_to_import_module/hello", expected_output=b"Hello\n")


def test_can_import_multiple_modules_from_module_using_from_import_syntax(chk_script_output):
    chk_script_output(script_path="script_using_from_to_import_multiple_modules/hello", expected_output=b"Hello\n")


def test_imported_modules_are_transformed(chk_script_output):
    chk_script_output(script_path="imports_in_imported_modules/hello", expected_output=b"Hello\n")


def test_circular_references_dont_cause_stack_overflow(chk_script_output):
    chk_script_output(script_path="circular_reference/hello", expected_output=b"Hello\n")


def test_explicit_relative_imports_with_single_dot_are_resolved_correctly(chk_script_output):
    chk_script_output(script_path="explicit_relative_import_single_dot/hello", expected_output=b"Hello\n")


def test_explicit_relative_imports_with_single_dot_in_package_init_are_resolved_correctly(chk_script_output):
    chk_script_output(script_path="explicit_relative_import_single_dot_in_init/hello", expected_output=b"Hello\n")


def test_explicit_relative_imports_from_parent_package_are_resolved_correctly(chk_script_output):
    chk_script_output(script_path="explicit_relative_import_from_parent_package/hello", expected_output=b"Hello\n")


def test_explicit_relative_imports_with_module_name_are_resolved_correctly(chk_script_output):
    chk_script_output(script_path="explicit_relative_import/hello", expected_output=b"Hello\n")


def test_explicit_relative_imports_with_module_name_in_package_init_are_resolved_correctly(chk_script_output):
    chk_script_output(script_path="explicit_relative_import_in_init/hello", expected_output=b"Hello\n")


def test_package_init_can_be_used_even_if_not_imported_explicitly(chk_script_output):
    chk_script_output(script_path="implicit_init_import/hello", expected_output=b"Hello\n")


def test_value_import_is_detected_when_import_is_renamed(chk_script_output):
    chk_script_output(script_path="import_from_as_value/hello", expected_output=b"Hello\n")


def test_module_import_is_detected_when_import_is_renamed(chk_script_output):
    chk_script_output(script_path="import_from_as_module/hello", expected_output=b"Hello\n")


def test_can_explicitly_set_python_interpreter(
    chk_script_output, run_shell_cmd, find_site_packages, venv_python_binary_path, find_script, tmp_path
):
    venv_path = os.path.join(tmp_path, "venv")
    # _shell.run(["virtualenv", venv_path])
    run_shell_cmd(["virtualenv", venv_path])
    site_packages_path = find_site_packages(venv_path)
    path_path = os.path.join(site_packages_path, "greetings.pth")
    with open(path_path, "w") as path_file:
        path_file.write(find_script("python_path_from_binary/packages\n"))

    chk_script_output(
        script_path="python_path_from_binary/hello",
        expected_output=b"Hello\n",
        python_binary=venv_python_binary_path(venv_path),
    )


def test_python_environment_variables_are_ignored_when_explicitly_setting_python_interpreter(
    chk_script_output, run_shell_cmd, find_site_packages, find_script, venv_python_binary_path, tmp_path
):
    venv_path = os.path.join(tmp_path, "venv")
    run_shell_cmd(["virtualenv", venv_path])
    site_packages_path = find_site_packages(venv_path)
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

        chk_script_output(
            script_path="python_path_from_binary/hello",
            expected_output=b"Hello\n",
            python_binary=venv_python_binary_path(venv_path),
        )
    finally:
        if original_python_path is None:
            del os.environ["PYTHONPATH"]
        else:
            os.environ["PYTHONPATH"] = original_python_path


@pytest.mark.skipif(sys.platform != "linux", reason="Windows python does not support shebang")
def test_can_explicitly_copy_shebang(chk_script_output):
    chk_script_output(
        script_path="script_with_special_shebang/hello",
        expected_output=b"1\n",
        copy_shebang=True,
    )


def test_modules_with_triple_quotes_can_be_bundled(chk_script_output):
    chk_script_output(script_path="module_with_triple_quotes/hello", expected_output=b"Hello\n'''\n\"\"\"\n")


def test_additional_python_modules_can_be_explicitly_included(chk_script_output):
    chk_script_output(
        script_path="script_with_dynamic_import/hello",
        expected_output=b"Hello\n",
        add_python_modules=("greeting",),
    )
