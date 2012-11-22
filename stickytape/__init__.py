import os.path
import re
import codecs

def script(path, add_python_paths=[], python_binary=None):
    python_paths = [os.path.dirname(path)] + add_python_paths + _read_sys_path_from_python_bin(python_binary)
    
    output = []
    
    output.append(_read_shebang(path))
    output.append(_prelude())
    output.append(_generate_module_writers(path, python_paths))
    output.append(_indent(open(path).read()))
    return "".join(output)

def _read_sys_path_from_python_bin(binary_path):
    if binary_path is None:
        return []
    else:
        output = subprocess.check_output(
            [binary_path, "-c", "import sys;\nfor path in sys.path: print path"],
            env={}
        )
        return [line.strip() for line in output.split("\n") if line.strip()]

def _indent(string):
    return "    " + string.replace("\n", "\n    ")

def _read_shebang(path):
    with open(path) as script_file:
        return script_file.readline()
    
def _prelude():
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path) as prelude_file:
        return prelude_file.read()

def _generate_module_writers(path, sys_path):
    generator = ModuleWriterGenerator(sys_path)
    generator.generate_for_file(path)
    return generator.build()

class ModuleWriterGenerator(object):
    def __init__(self, sys_path):
        self._sys_path = sys_path
        self._modules = {}
    
    def build(self):
        output = []
        for module_path, module_source in self._modules.iteritems():
            output.append("    __stickytape_write_module({0}, {1})\n".format(
                _string_escape(module_path),
                _string_escape(module_source)
            ))
        return "".join(output)
    
    def generate_for_file(self, python_file_path):
        with open(python_file_path) as python_file:
            module_writing_output = []
            for line in python_file:
                module_writer = self._generate_for_line(line)
    
    def _generate_for_line(self, line):
        import_line = _read_import_line(line)
        if import_line is not None and not _is_stlib_import(import_line):
            self._generate_for_import(import_line)

    def _generate_for_import(self, import_line):
        import_targets = self._read_possible_import_targets(import_line)
        
        for import_target in import_targets:
            if import_target.module_path not in self._modules:
                self._modules[import_target.module_path] = import_target.source
                self.generate_for_file(import_target.absolute_path)
    
    def _read_possible_import_targets(self, import_line):
        possible_module_paths = [
            import_line.import_path + ".py",
            os.path.join(import_line.import_path, "__init__.py")
        ]
        for item in import_line.items:
            possible_module_paths += [
                os.path.join(import_line.import_path, item + ".py"),
                os.path.join(import_line.import_path, item, "__init__.py")
            ]
        
        import_targets = [
            self._find_module(module_path)
            for module_path in possible_module_paths
        ]
        
        valid_import_targets = [target for target in import_targets if target is not None]
        if len(valid_import_targets) > 0:
            return valid_import_targets
        else:
            raise RuntimeError("Could not find module: " + import_line.import_path)

    def _find_module(self, module_path):
        for sys_path in self._sys_path:
            full_module_path = os.path.join(sys_path, module_path)
            if os.path.exists(full_module_path):
                return ImportTarget(full_module_path, module_path, _read_file(full_module_path))
        return None
        
def _read_import_line(line):
    package_pattern = r"([^\s.]+(?:\.[^\s.]+)*)"
    result = re.match("^import " + package_pattern + "$", line.strip())
    if result:
        return ImportLine(result.group(1).replace(".", "/"), [])
    
    result = re.match("^from " + package_pattern + r" import ([^\s.]+(?:\s*,\s*[^\s.]+)*)$", line.strip())
    if result:
        items = re.split(r"\s*,\s*", result.group(2))
        return ImportLine(result.group(1).replace(".", "/"), items)
    
    return None

def _read_file(path):
    with open(path) as file:
        return file.read()

def _string_escape(string):
    return "'''{0}'''".format(codecs.getencoder("string_escape")(string)[0])

# TODO: fill out, either by hand or generatively
_stdlib_modules = [
    "argparse",
    "codecs", "contextlib",
    "errno",
    "functools",
    "hashlib",
    "os", "os/path",
    "re",
    "shutil", "subprocess", "sys",
    "tempfile", "time",
    "urlparse"
]

def _is_stlib_import(import_line):
    return import_line.import_path in _stdlib_modules

class ImportTarget(object):
    def __init__(self, absolute_path, module_path, source):
        self.absolute_path = absolute_path
        self.module_path = module_path
        self.source = source

class ImportLine(object):
    def __init__(self, import_path, items):
        self.import_path = import_path
        self.items = items
        
