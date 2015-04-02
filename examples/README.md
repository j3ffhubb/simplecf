This is a trivial example of simplecf using the recommended folder structure.

Some example invocations:

```
# Show the data file after all IMPORT directives are processed
simple-cf.py -d data_files/TestStack_us-west-2.json --show

# Create a stack
simple-cf.py -d data_files/TestStack_us-west-2.json --create

# Show a diff of the currently running stack and the current version
# of the template
simple-cf.py -d data_files/TestStack_us-west-2.json --diff
```

