stickytape: Convert Python packages into a single script
========================================================

Stickytape can be used to convert a Python script and any Python modules
it depends on into a single-file Python script.

Since this relies on correctly analysing both your script and any dependent modules,
this may not work correctly in all circumstances.
I bodged together the code a long time ago for a specific use case I had,
so many normal uses of Python imports are not properly supported.
If you need to create a standalone executable from your Python script,
I recommend using an alternative such as `PyInstaller <http://www.pyinstaller.org/>`_.

Installation
------------

::

    pip install stickytape

Usage
-----

You can tell stickytape which directories to search using the ``--add-python-path`` argument.
For instance:

.. code:: sh

    stickytape scripts/blah --add-python-path . > /tmp/blah-standalone

Or to output directly to a file:

.. code:: sh

    stickytape scripts/blah --add-python-path . --output-file /tmp/blah-standalone

You can also point stickytape towards a Python binary that it should use
sys.path from, for instance the Python binary inside a virtualenv:

.. code:: sh

    stickytape scripts/blah --python-binary _virtualenv/bin/python --output-file /tmp/blah-standalone

Stickytape cannot automatically detect dynamic imports,
but you can use ``--add-python-module`` to explicitly include modules:

.. code:: sh

    stickytape scripts/blah --add-python-module blah.util

By default, stickytape will ignore the shebang in the script
and use ``"#!/usr/bin/env python"`` in the output file.
To copy the shebang from the original script,
use ``--copy-shebang``:

.. code:: sh

    stickytape scripts/blah --copy-shebang --output-file /tmp/blah-standalone

As you might expect with a program that munges source files, there are a
few caveats:

-  Due to the way that stickytape generates the output file, your script
   source file should be encoded using UTF-8. If your script doesn't declare
   its encoding in its first two lines, then it will be UTF-8 by default
   as of Python 3.

-  Your script shouldn't have any ``from __future__`` imports.

-  Anything that relies on the specific location of files will probably
   no longer work. In other words, ``__file__`` probably isn't all that
   useful.

-  Any files that aren't imported won't be included. Static data that
   might be part of your project, such as other text files or images,
   won't be included.
