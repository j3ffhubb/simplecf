-  `What is simplecf? <#what-is-simplecf>`__
-  `How to use <#how-to-use>`__

What is simplecf?
~~~~~~~~~~~~~~~~~

simplecf is a templating system for AWS Cloudformation that allows you
to make many variations of a single template for maximum code re-use.
See a simple example `HERE  <https://github.com/j3ffhubb/simplecf/tree/master/examples/>`_

The standard use-case is that you have 4 environments {dev,qa,stage,prod}
based on one Cloudformation template.  Rather than maintaining 4 templates
that are mostly identical, you can add Mustache {{ tags }} to your templates
and create simple JSON data files that specify the values.  This has
the added benefit of eliminating the need for a lot of boilerplate mapping
code in the "Parameters" section of your templates.

simplecf also supports data file fragments;  You can create a single data
file for each AWS region that contain region-specific data like ami-id,
etc... and import that data file fragment into your other templates.

How to use
~~~~~~~~~~

You can install using pip:

::

    #As root, or alternately use --user
    pip install simplecf

Create a standard AWS Cloudformation template, adding Mustache {{ tags
}} for the parts you wish to be dynamically substituted

my-cf-template.json:

::

    ...
    "Tags":[
      {"Key": "Phase", "Value": "{{ phase }}"}
    ]
    ...

Next, create a JSON file to define the stack and fill in the tags. You
can generate an empty data file with
``simplecf.py -d prod.json -c my-cf-template.json``

prod.json:

::

    {
      "CF_TEMPLATE": "my-cf-template.json",
      "STACK_NAME": "MyStackProd",
      "STACK_REGION": "us-east-1",
      "phase": "Prod"
    }

Then run simplecf to generate the template

``simplecf.py -d prod.json``

Which outputs:

MyStackProd.json:

::

    ...
    "Tags":[
      {"Key": "Phase", "Value": "Prod"}
    ]
    ...

Run simplecf.py with --help to see various other tools and options.
