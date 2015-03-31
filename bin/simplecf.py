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
import difflib
import os
import pystache
import json
import argparse


def get_cf_conn(stack_region):
    try:
        return cloudformation.connect_to_region(stack_region)
    except Exception as ex:
        print("Error connecting to AWS, please ensure that you've "
            "exported the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY "
            "environment variables with valid keys that have permission "
            "to use Cloudformation.")
        print(ex)
        exit(1)

def fetch_stack_template(stack_name, stack_region):
    conn = get_cf_conn(stack_region)
    return conn.get_template(stack_name)

def diff_local_and_remote(data_file):
    data_json, local = escape_template(data_file, write=False)
    local = json_clean(local)
    remote = json_clean(
        fetch_stack_template(
            data_json["STACK_NAME"], data_json["STACK_REGION"]))
    diff = difflib.unified_diff(remote, local, "REMOTE", "LOCAL")
    print("\n".join(diff))

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

def escape_template(data_file, write=True):
    data_json = json_load(data_file)
    cf_template = data_json["CF_TEMPLATE"]
    cf_text = read_file_text(cf_template)
    result = pystache.render(cf_text, data_json)
    if write:
        outfile = "{0}.json".format(data_json["STACK_NAME"])
        write_file_text(outfile, result)
        print("Created {0}".format(outfile))
    else:
        return data_json, result

def update_stack(data_file, create=False):
    data_json, result = escape_template(data_file, write=False)
    conn = get_cf_conn(data_json["STACK_REGION"])
    if create:
        conn.create_stack(data_json["STACK_NAME"], result)
    else:
        conn.update_stack(data_json["STACK_NAME"], result)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--data-file", dest="data_file",
        help="This specifies the JSON data file containing the "
        "stack definition")
    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument(
        "--diff", dest="diff",
        help="Print the unified diff of the local template vs. the "
        "template that was used to create the current version of "
        "the stack")
    me_group.add_argument(
        "--update", dest="update",
        help="Directly update the Cloudformation stack associated with -d")
    me_group.add_argument(
        "--create", dest="create",
        help="Directly create the Cloudformation stack associated with -d")
    args = parser.parse_args()
    if not args.data_file:
        print("Error:  Must specify -d")
        exit(1)
    if args.diff:
        diff_local_and_remote(args.data_file)
    elif args.update:
        update_stack(args.data_file)
    elif args.create:
        update_stack(args.data_file, create=True)
    else:
        escape_template(args.data_file)

main()
