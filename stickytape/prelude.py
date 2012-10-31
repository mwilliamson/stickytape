import tempfile as __stickytape_tempfile
import contextlib as __stickytape_contextlib
import shutil as __stickytape_shutil

@__stickytape_contextlib.contextmanager
def __stickytape_temporary_dir():
    dir_path = __stickytape_tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        __stickytape_shutil.rmtree(dir_path)

with __stickytape_temporary_dir() as __stickytape_working_dir:
    def __stickytape_write_module(path, contents):
        import os, os.path, errno
        
        path = os.path.join(__stickytape_working_dir, path)

        def mkdir_p(path):
            try:
                os.makedirs(path)
            except OSError as exception:
                if exception.errno == errno.EEXIST:
                    pass
                else:
                    raise
                    
        mkdir_p(os.path.dirname(path))
        
        with open(path, "w") as module_file:
            module_file.write(contents)

    import sys as __stickytape_sys
    __stickytape_sys.path.insert(0, __stickytape_working_dir)
