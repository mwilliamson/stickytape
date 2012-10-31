import os.path
import re
import codecs

def script(path, python_paths=[]):
    output = []
    
    sys_path = [os.path.dirname(path)] + python_paths
    
    output.append(_read_shebang(path))
    output.append(_prelude())
    output.append(_generate_module_writers(path, sys_path))
    output.append(_indent(open(path).read()))
    return "".join(output)

def _indent(string):
    return "    " + string.replace("\n", "\n    ")

def _read_shebang(path):
    with open(path) as script_file:
        return script_file.readline()
    
def _prelude():
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path) as prelude_file:
        return prelude_file.read()

def _generate_module_writers(python_file_path, sys_path):
    with open(python_file_path) as python_file:
        module_writing_output = []
        for line in python_file:
            module_writer = _transform_line(line, sys_path)
            if module_writer is not None:
                module_writing_output.extend(module_writer)
        
        return "".join(module_writing_output)
    

def _transform_line(line, sys_path):
    import_line = _read_import_line(line)
    if import_line is None or _is_stlib_import(import_line):
        return None
    else:
        return _transform_import(import_line, sys_path)
        
def _read_import_line(line):
    package_pattern = "([^\s.]+(?:\.[^\s.]+)*)"
    result = re.match("^import " + package_pattern + "$", line.strip())
    if result:
        return ImportLine(result.group(1).replace(".", "/"), None)
    
    result = re.match("^from " + package_pattern +" import ([^\s.]+)$", line.strip())
    if result:
        return ImportLine(result.group(1).replace(".", "/"), result.group(2))
    
    return None

def _transform_import(import_line, sys_path):
    import_targets = _read_possible_import_targets(import_line, sys_path)
    
    output = []
    
    for import_target in import_targets:
        output.append( "    __stickytape_write_module({0}, {1})\n".format(
            _string_escape(import_target.module_path),
            _string_escape(import_target.source)
        ))
        output.append(_generate_module_writers(import_target.absolute_path, sys_path))
    return "".join(output)
    
def _read_possible_import_targets(import_line, sys_paths):
    possible_module_paths = [
        import_line.import_path + ".py",
        os.path.join(import_line.import_path, "__init__.py")
    ]
    if import_line.item is not None:
        possible_module_paths += [
            os.path.join(import_line.import_path, import_line.item + ".py"),
            os.path.join(import_line.import_path, import_line.item, "__init__.py")
        ]
    
    import_targets = [
        _find_module(module_path, sys_paths)
        for module_path in possible_module_paths
    ]
    
    valid_import_targets = [target for target in import_targets if target is not None]
    if len(valid_import_targets) > 0:
        return valid_import_targets
    else:
        raise RuntimeError("Could not find module: " + import_line.import_path)

def _find_module(module_path, sys_paths):
    for sys_path in sys_paths:
        full_module_path = os.path.join(sys_path, module_path)
        if os.path.exists(full_module_path):
            return ImportTarget(full_module_path, module_path, _read_file(full_module_path))
    return None

def _read_file(path):
    with open(path) as file:
        return file.read()

def _string_escape(string):
    return "'''{0}'''".format(codecs.getencoder("string_escape")(string)[0])

# TODO: fill out, either by hand or generatively
_stdlib_modules = ["argparse", "codecs", "contextlib", "errno", "functools", "hashlib", "os", "os/path", "re", "shutil", "subprocess", "sys", "tempfile"]

def _is_stlib_import(import_line):
    return import_line.import_path in _stdlib_modules

class ImportTarget(object):
    def __init__(self, absolute_path, module_path, source):
        self.absolute_path = absolute_path
        self.module_path = module_path
        self.source = source

class ImportLine(object):
    def __init__(self, import_path, item):
        self.import_path = import_path
        self.item = item
        
