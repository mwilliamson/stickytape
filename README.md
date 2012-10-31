# stickytape: Convert Python packages into a single script

Stickytape can be used to convert a Python script and any Python modules it
depends into a single-file Python script. You can tell stickytape which
directories to search using the `--add-python-path` argument. For instance:

```stickytape scripts/blah --add-python-path . > /tmp/blah-standalone```
