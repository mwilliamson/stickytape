import ast
import os.path
import subprocess

from .stdlib import is_stdlib_module


def script(
    path,
    add_python_modules=None,
    add_python_paths=None,
    python_binary=None,
    copy_shebang=False,
):
    if add_python_modules is None:
        add_python_modules = []

    if add_python_paths is None:
        add_python_paths = []

    python_paths = [os.path.dirname(path)] + add_python_paths + _read_sys_path_from_python_bin(python_binary)

    output = []

    output.append(_generate_shebang(path, copy=copy_shebang))
    output.append(_prelude())
    output.append(_generate_module_writers(
        path,
        sys_path=python_paths,
        add_python_modules=add_python_modules,
    ))
    with _open_source_file(path) as source_file:
        output.append(_indent(source_file.read()))
    return "".join(output)

def _read_sys_path_from_python_bin(binary_path):
    if binary_path is None:
        return []
    else:
        output = subprocess.check_output(
            [binary_path, "-E", "-c", "import sys;\nfor path in sys.path: print(path)"],
        )
        return [
            # TODO: handle non-UTF-8 encodings
            line.strip().decode("utf-8")
            for line in output.split(b"\n")
            if line.strip()
        ]

def _indent(string):
    return "    " + string.replace("\n", "\n    ")

def _generate_shebang(path, copy):
    if copy:
        with _open_source_file(path) as script_file:
            first_line = script_file.readline()
            if first_line.startswith("#!"):
                return first_line

    return "#!/usr/bin/env python"

def _prelude():
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path, encoding="utf-8") as prelude_file:
        return prelude_file.read()

def _generate_module_writers(path, sys_path, add_python_modules):
    generator = ModuleWriterGenerator(sys_path)
    generator.generate_for_file(path, add_python_modules=add_python_modules)
    return generator.build()

class ModuleWriterGenerator(object):
    def __init__(self, sys_path):
        self._sys_path = sys_path
        self._modules = {}

    def build(self):
        output = []
        for module_path, module_source in self._modules.values():
            output.append("    __stickytape_write_module({0}, {1})\n".format(
                repr(module_path),
                repr(module_source)
            ))
        return "".join(output)

    def generate_for_file(self, python_file_path, add_python_modules):
        self._generate_for_module(ImportTarget(python_file_path, relative_path=None, is_package=False, module_name=None))

        for add_python_module in add_python_modules:
            import_line = ImportLine(module_name=add_python_module, items=[])
            self._generate_for_import(python_module=None, import_line=import_line)

    def _generate_for_module(self, python_module):
        import_lines = _find_imports_in_module(python_module)
        for import_line in import_lines:
            if not _is_stdlib_import(import_line):
                self._generate_for_import(python_module, import_line)

    def _generate_for_import(self, python_module, import_line):
        import_targets = self._read_possible_import_targets(python_module, import_line)

        for import_target in import_targets:
            if import_target.module_name not in self._modules:
                self._modules[import_target.module_name] = (import_target.relative_path, import_target.read_binary())
                self._generate_for_module(import_target)

    def _read_possible_import_targets(self, python_module, import_line):
        module_name_parts = import_line.module_name.split(".")

        module_names = [
            ".".join(module_name_parts[0:index + 1])
            for index in range(len(module_name_parts))
        ] + [
            import_line.module_name + "." + item
            for item in import_line.items
        ]

        import_targets = [
            self._find_module(module_name)
            for module_name in module_names
        ]

        valid_import_targets = [target for target in import_targets if target is not None]
        return valid_import_targets
        # TODO: allow the user some choice in what happens in this case?
        # Detection of try/except blocks is possibly over-complicating things
        #~ if len(valid_import_targets) > 0:
            #~ return valid_import_targets
        #~ else:
            #~ raise RuntimeError("Could not find module: " + import_line.import_path)

    def _find_module(self, module_name):
        for sys_path in self._sys_path:
            for is_package in (True, False):
                if is_package:
                    suffix = "/__init__.py"
                else:
                    suffix = ".py"

                relative_path = module_name.replace(".", "/") + suffix
                full_module_path = os.path.join(sys_path, relative_path)
                if os.path.exists(full_module_path):
                    return ImportTarget(
                        full_module_path,
                        relative_path=relative_path,
                        is_package=is_package,
                        module_name=module_name,
                    )
        return None


def _find_imports_in_module(python_module):
    source = _read_binary(python_module.absolute_path)
    parse_tree = ast.parse(source, python_module.absolute_path)

    for node in ast.walk(parse_tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                yield ImportLine(name.name, [])

        if isinstance(node, ast.ImportFrom):
            if node.level == 0:
                module = node.module
            else:
                level = node.level

                if python_module.is_package:
                    level -= 1

                if level == 0:
                    package_name = python_module.module_name
                else:
                    package_name = ".".join(python_module.module_name.split(".")[:-level])

                if node.module is None:
                    module = package_name
                else:
                    module = package_name + "." + node.module

            yield ImportLine(module, [name.name for name in node.names])


def _read_binary(path):
    with open(path, "rb") as file:
        return file.read()


def _open_source_file(path):
    return open(path, "rt", encoding="utf-8")


def _is_stdlib_import(import_line):
    return is_stdlib_module(import_line.module_name)

class ImportTarget(object):
    def __init__(self, absolute_path, relative_path, is_package, module_name):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.is_package = is_package
        self.module_name = module_name

    def read_binary(self):
        return _read_binary(self.absolute_path)

class ImportLine(object):
    def __init__(self, module_name, items):
        self.module_name = module_name
        self.items = items
