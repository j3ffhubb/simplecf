"""

"""

import json
import os
import sys
import unittest

if sys.version_info < (3, 0):
    from commands import getstatusoutput
else:
    from subprocess import getstatusoutput

CWD = os.path.abspath(os.path.dirname(__file__))
EXE = os.path.join(CWD, 'bin', 'simplecf.py')
EXAMPLES = os.path.join(CWD, 'examples')
DATA_FILE = os.path.join(EXAMPLES, 'data_files', 'TestStack_us-west-2.json')

def _cmd(args):
    command = EXE + ' ' + args
    status, output = getstatusoutput(command)
    assert not status, command
    return status, output

def _create():
    _cmd("-d '{0}'".format(DATA_FILE))
    path = 'TestStack.json'
    with open(path) as f:
        result = json.load(f)
    os.remove(path)
    return result

def _show():
    status, output = _cmd("-d '{0}' --show".format(DATA_FILE))
    return json.loads(output)

class TestsUnit(unittest.TestCase):
    def test_create(self):
        result = _create()
        properties = result['Resources']['EC2Instance']['Properties']
        for value, expected in (
            (properties['InstanceType'], 't2.micro'),
            (properties['ImageId'], 'ami-4dbf9e7d'),
            (properties['Tags'][0]['Value'], 'Prod'),
        ):
            self.assertEqual(value, expected)

    def test_show(self):
        """ Mostly tests "IMPORT": [...]
        """
        result = _show()
        for k, v in {
            "CF_TEMPLATE": "../cf_templates/single_instance.json",
            "STACK_NAME": "TestStack",
            "STACK_REGION": "us-west-2",
            "cidr_ip": "0.0.0.0/0",
            "image_id": "ami-4dbf9e7d",
            "instance_key_name": "YOUR_SSH_KEY_NAME",
            "instance_type": "t2.micro",
            "phase": "Prod"
        }.items():
            self.assertIn(k, result)
            self.assertEqual(result[k], v)

@unittest.skipUnless(
    all(os.getenv(x) for x in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')),
    'No AWS access key pair specified')
class TestsIntegration(unittest.TestCase):
    pass
