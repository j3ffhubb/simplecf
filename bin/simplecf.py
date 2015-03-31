#!/usr/bin/env python
"""
This file is part of the simplecf project, Copyright simplecf Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

from boto import cloudformation
import collections
import os
import pystache
import json
import argparse

def fetch_stack_template(stack_name, stack_region):
    conn = cloudformation.connect_to_region(stack_region)
    template = conn.get_template(stack_name)
    return json_clean(template)

def json_clean(json_str):
    json_data = json.loads(json_str)
    return json.dumps(
        json_data, indent=4, separators=(":", ","), sort_keys=True)

def json_load(path):
    check_file_exists(path)
    with open(path) as file_handle:
        return json.load(file_handle)

def check_file_exists(path):
    if not os.path.isfile(path):
        print("Error:  {0} does not exist".format(path))
        exit(1)

def read_file_text(path):
    check_file_exists(path)
    with open(path) as file_handle:
        return file_handle.read()

def write_file_text(path, text):
    with open(path, "w") as file_handle:
        file_handle.write(text)

def validate_data_file(path):
    raise NotImplementedError

def escape_template(data_file):
    data_json = json_load(data_file)
    cf_template = data_json["CF_TEMPLATE"]
    cf_text = read_file_text(cf_template)
    result = pystache.render(cf_text, data_json)
    outfile = "{0}.json".format(data_json["STACK_NAME"])
    write_file_text(outfile, result)
    print("Created {0}".format(outfile))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data-file", dest="data_file")
    args = parser.parse_args()
    if not args.data_file:
        print("Error:  Must specify -d")
        exit(1)
    escape_template(args.data_file)

main()