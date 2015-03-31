#Warning, pre-alpha software, don't use

#What is simplecf?

simplecf is a templating system for AWS Cloudformation, similar to Cumulus.

#Why not use Cumulus?

Cumulus is good, but I prefer something based on a more traditional templating language like Mustache, that doesn't attempt to ensure the source template still builds something valid even without Cumulus (a bad design constraint IMHO).  Cumulus accepts Mustache-style tags, but can only accept them as environment variables, and not in the Yaml files.  A pure templating-language approach is much simpler, and much easier to understand.  Rather than using 2 different data formats (JSON and YAML), simplecf uses only JSON.

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
Next, create a JSON file to define the stack and fill in the tags

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
