import ast
import codecs
import os.path
import posixpath
import subprocess
import sys

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
    output.append(_indent(open(path).read()))
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
        with open(path) as script_file:
            first_line = script_file.readline()
            if first_line.startswith("#!"):
                return first_line

    return "#!/usr/bin/env python"

def _prelude():
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path) as prelude_file:
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
        for module_path, module_source in _iteritems(self._modules):
            output.append("    __stickytape_write_module({0}, {1})\n".format(
                _string_escape(module_path),
                _string_escape(module_source)
            ))
        return "".join(output)

    def generate_for_file(self, python_file_path, add_python_modules):
        self._generate_for_module(ImportTarget(python_file_path, "."))

        for add_python_module in add_python_modules:
            import_line = ImportLine(module_name=add_python_module, items=[])
            self._generate_for_import(python_module=None, import_line=import_line)

    def _generate_for_module(self, python_module):
        import_lines = _find_imports_in_file(python_module.absolute_path)
        for import_line in import_lines:
            if not _is_stdlib_import(import_line):
                self._generate_for_import(python_module, import_line)

    def _generate_for_import(self, python_module, import_line):
        import_targets = self._read_possible_import_targets(python_module, import_line)

        for import_target in import_targets:
            if import_target.module_path not in self._modules:
                self._modules[import_target.module_path] = import_target.read()
                self._generate_for_module(import_target)

    def _read_possible_import_targets(self, python_module, import_line):
        import_path = _resolve_package_to_import_path(import_line.module_name)
        import_path_parts = import_path.split("/")
        possible_init_module_paths = [
            posixpath.join(posixpath.join(*import_path_parts[0:index + 1]), "__init__.py")
            for index in range(len(import_path_parts))
        ]

        possible_module_paths = [import_path + ".py"] + possible_init_module_paths

        for item in import_line.items:
            possible_module_paths += [
                posixpath.join(import_path, item + ".py"),
                posixpath.join(import_path, item, "__init__.py")
            ]

        import_targets = [
            self._find_module(python_module, module_path)
            for module_path in possible_module_paths
        ]

        valid_import_targets = [target for target in import_targets if target is not None]
        return valid_import_targets
        # TODO: allow the user some choice in what happens in this case?
        # Detection of try/except blocks is possibly over-complicating things
        #~ if len(valid_import_targets) > 0:
            #~ return valid_import_targets
        #~ else:
            #~ raise RuntimeError("Could not find module: " + import_line.import_path)

    def _find_module(self, importing_python_module, module_path):
        if importing_python_module is not None:
            relative_module_path = os.path.join(os.path.dirname(importing_python_module.absolute_path), module_path)
            if os.path.exists(relative_module_path):
                return ImportTarget(relative_module_path, os.path.join(os.path.dirname(importing_python_module.module_path), module_path))

        for sys_path in self._sys_path:
            full_module_path = os.path.join(sys_path, module_path)
            if os.path.exists(full_module_path):
                return ImportTarget(full_module_path, module_path)
        return None


def _find_imports_in_file(file_path):
    source = _read_file(file_path)
    parse_tree = ast.parse(source, file_path)

    for node in ast.walk(parse_tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                yield ImportLine(name.name, [])

        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                module = "."
            else:
                module = node.module
            yield ImportLine(module, [name.name for name in node.names])


def _resolve_package_to_import_path(package):
    import_path = package.replace(".", "/")
    if import_path.startswith("/"):
        return "." + import_path
    else:
        return import_path

def _read_file(path):
    with open(path) as file:
        return file.read()

def _is_stdlib_import(import_line):
    return is_stdlib_module(import_line.module_name)

class ImportTarget(object):
    def __init__(self, absolute_path, module_path):
        self.absolute_path = absolute_path
        self.module_path = posixpath.normpath(module_path.replace("\\", "/"))

    def read(self):
        return _read_file(self.absolute_path)

class ImportLine(object):
    def __init__(self, module_name, items):
        self.module_name = module_name
        self.items = items


if sys.version_info[0] == 2:
    _iteritems = lambda x: x.iteritems()

    def _string_escape(string):
        return "'''{0}'''".format(codecs.getencoder("string_escape")(string)[0].decode("ascii"))

else:
    _iteritems = lambda x: x.items()

    _string_escape = repr
