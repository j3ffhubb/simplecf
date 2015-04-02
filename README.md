#What is simplecf?

simplecf is a templating system for AWS Cloudformation, similar to Cumulus.

#Why not use Cumulus?

Cumulus is good, but I prefer something based on a more traditional templating language like Mustache, that doesn't attempt to ensure the source template still builds something valid even without Cumulus (a bad design constraint IMHO).  Cumulus accepts Mustache-style tags, but can only accept them as environment variables, and not in the Yaml files.

A pure templating-language approach is simpler and easier to maintain, because the data file only has to do naive substitution of tags, instead of mimicking the structure of the Cloudformation template.  This also means that you could conceivably re-use data files between completely disparate templates, and eliminate a lot of boilerplate mapping code in the "Parameters" section of your templates.

#How to use

Create a standard AWS Cloudformation template, adding Mustache {{ tags }} for the parts you wish to be dynamically substituted

my-cf-template.json:

```
...
"Tags":[
  {"Key": "Phase", "Value": "{{ phase }}"}
]
...
```
Next, create a JSON file to define the stack and fill in the tags.  You can generate an empty data file with `simplecf.py -d prod.json -c my-cf-template.json`

prod.json:

```
{
  "CF_TEMPLATE": "my-cf-template.json",
  "STACK_NAME": "MyStackProd",
  "STACK_REGION": "us-east-1",
  "phase": "Prod"
}
```

Then run simplecf to generate the template

`simplecf.py -d prod.json`

Which outputs:

MyStackProd.json:

```
...
"Tags":[
  {"Key": "Phase", "Value": "Prod"}
]
...
```

Run simplecf.py with --help to see various other tools and options.
