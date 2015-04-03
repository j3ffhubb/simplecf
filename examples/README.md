This is a trivial example of simplecf using the recommended folder structure.

The "phase" and "region" folders contain incomplete data files that data files in the "data\_files" folder use with their "IMPORT" directives.  For example, region/us-west-2.json contains a RHEL7 AMI-ID and other data that is specific to a region.  Using this strategy, you should be able to eliminate most or all of your boilerplate mapping code in the "Properties" section of your Cloudformation templates by moving it into simplecf data files.

The "cf\_templates" folder contains Cloudformation templates with Mustache {{ tags }} that correspond to the keys in the data files, which are substituted with the values in the data files.

Any data file that is specified in the -d argument of simplecf.py must contain these mandatory key/values:

```
CF_TEMPLATE:  The relative path of the Cloudformation template from the data file
STACK_NAME:  The name of the stack to create/update in Cloudformation (must be unique per-region)
STACK_REGION:  The region to create/update the stack in (us-east-1, us-west-2, etc...)
```

simplecf will check that all tags were substituted before performing any action, and will print a warning if any of the substituted values are empty strings.


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

