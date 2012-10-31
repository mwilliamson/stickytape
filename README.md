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
