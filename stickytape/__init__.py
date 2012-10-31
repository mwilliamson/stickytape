import os.path
import re
import codecs

def script(path):
    output = []
    
    sys_path = [os.path.dirname(path)]
    
    with open(path) as script_file:
        _add_shebang(script_file, output)
        _add_prelude(script_file, output)
        _add_body(script_file, output, sys_path)
        return "".join(output)

def _add_shebang(script_file, output):
    output.append(script_file.readline())
    
def _add_prelude(script_file, output):
    prelude_path = os.path.join(os.path.dirname(__file__), "prelude.py")
    with open(prelude_path) as prelude_file:
        output.append(prelude_file.read())

def _add_body(script_file, output, sys_path):
    body_output = []
    for line in script_file:
        body_output.append(_transform(line, sys_path))
        
    output.append("    " + "".join(body_output).replace("\n", "\n    "))

def _transform(line, sys_path):
    import_line = _read_import_line(line)
    if import_line is None or _is_stlib_import(import_line):
        return line
    else:
        return _transform_import(import_line, sys_path)
        
def _read_import_line(line):
    result = re.match("^import ([^\s.]+)$", line.strip())
    if result:
        return ImportLine(line, result.group(1).replace(".", "/"))
    else:
        return None

def _transform_import(import_line, sys_path):
    module_path, module_source = _read_import_target(import_line, sys_path)
    write_module = "__stickytape_write_module({0}, {1})".format(
        _string_escape(module_path),
        _string_escape(module_source)
    )
    return "{0}\n{1}".format(write_module, import_line.original_string)
    
def _read_import_target(import_line, sys_paths):
    for sys_path in sys_paths:
        module_paths = [
            import_line.import_path + ".py",
            os.path.join(import_line.import_path, "__init__.py")
        ]
        for module_path in module_paths:
            full_module_path = os.path.join(sys_path, module_path)
            if os.path.exists(full_module_path):
                return module_path, _read_file(full_module_path)
                
    raise RuntimeError("Could not find module: " + import_line.import_path)

def _read_file(path):
    with open(path) as file:
        return file.read()

def _string_escape(string):
    return "'''{0}'''".format(codecs.getencoder("string_escape")(string)[0])

# TODO: fill out, either by hand or generatively
_stdlib_modules = ["hashlib"]

def _is_stlib_import(import_line):
    return import_line.import_path in _stdlib_modules

class ImportLine(object):
    def __init__(self, original_string, import_path):
        self.original_string = original_string
        self.import_path = import_path
        
