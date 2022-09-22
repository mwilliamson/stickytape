import pytest
import os
import sys
import platform
import shutil
import tempfile
import subprocess
import contextlib
import re
import stat


import stickytape
from test_scripts import root as test_script_root


@pytest.fixture(scope="session")
def temporary_script(tmp_path_factory: pytest.TempPathFactory):
    fn = tmp_path_factory.mktemp("script_dir") / "script"

    def _temporary_script(contents):
        with open(fn, "w") as script_file:
            script_file.write(contents)

        st = os.stat(fn)
        fn.chmod(st.st_mode | stat.S_IEXEC)
        return fn

    return _temporary_script


@pytest.fixture
def capture_stdout(monkeypatch) -> dict:
    buffer = {"stdout": "", "write_calls": 0}

    def fake_write(s):
        buffer["stdout"] += s
        buffer["write_calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", fake_write)
    return buffer


@pytest.fixture(scope="session")
def run_shell_cmd() -> bytes:
    def run_shell(cmd) -> str:
        # run shell command
        # myenv = os.environ.copy()
        # pypath = ''
        # p_sep = ':' if is_windows else ';'
        # for d in sys.path:
        #     pypath = pypath + d + p_sep
        # myenv['PYTHONPATH'] = pypath
        # result = subprocess.run(cmd, env=myenv, stdout=subprocess.PIPE)
        # result = subprocess.run(cmd, env=myenv, capture_output=True, shell=True)
        # return result.stdout
        result = subprocess.check_output(cmd)
        return result

    return run_shell


@pytest.fixture(scope="session")
def chk_script_output(find_script, run_shell_cmd, is_windows, temporary_script):
    def script_output(script_path, expected_output, expected_modules=None, **kwargs):
        result = stickytape.script(find_script(script_path), **kwargs)

        if expected_modules is not None:
            actual_modules = set(re.findall(r"__stickytape_write_module\('([^']*)\.py'", result))
            assert set(expected_modules) == actual_modules

        script_file_path = str(temporary_script(result))
        # with temporary_script(result) as script_file_path:
        try:
            if is_windows:
                command = [sys.executable, script_file_path]
            else:
                command = [script_file_path]
            output = run_shell_cmd(command).replace(b"\r\n", b"\n")
        except:
            for index, line in enumerate(result.splitlines()):
                print((index + 1), line)
            raise
        assert expected_output == output

    return script_output


@pytest.fixture(scope="session")
def find_script():
    def _find_script(path):
        return os.path.join(test_script_root, path)

    return _find_script


@pytest.fixture(scope="session")
def is_windows():
    return platform.system() == "Windows"


@pytest.fixture(scope="session")
def find_site_packages():
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

    return _find_site_packages


@pytest.fixture(scope="session")
def venv_python_binary_path(is_windows):
    def _venv_python_binary_path(venv_path):
        if is_windows:
            bin_directory = "Scripts"
        else:
            bin_directory = "bin"

        return os.path.join(venv_path, bin_directory, "python")

    return _venv_python_binary_path
