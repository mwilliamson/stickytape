# stickytape: Convert Python packages into a single script

Stickytape can be used to convert a Python script and any Python modules it
depends into a single-file Python script. You can tell stickytape which
directories to search using the `--add-python-path` argument. For instance:

```stickytape scripts/blah --add-python-path . > /tmp/blah-standalone```

Or to output directly to a file:

```stickytape scripts/blah --add-python-path . --output-file /tmp/blah-standalone```

You can also point stickytape towards a Python binary that it should use sys.path
from, for instance the Python binary inside a virtualenv:

```stickytape scripts/blah --python-binary _virtualenv/bin/python --output-file /tmp/blah-standalone```

As you might expect with a program that munges source files, there are a few
caveats:

* Detection of imports is done using a fairly simple regex. For instance, things
  will go horribly wrong if you use have two import statements on the same line
  separated by a semi-colon. Similarly, imports using importlib won't be
  detected.
  
* Anything that relies on the specific location of files will probably no longer work. In
  other words, `__file__` probably isn't all that useful.
  
* Any files that aren't imported won't be included. Static data that might be
  part of your project, such as other text files or images, won't be included.
