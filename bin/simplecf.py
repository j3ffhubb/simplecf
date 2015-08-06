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

import boto
from boto import cloudformation
import collections
import difflib
import os
import re
import pystache
import json
import argparse
import time

__version__ = "1.0.2"

ORIG_WD = os.getcwd()

REQUIRED_TAGS = ("CF_TEMPLATE", "STACK_NAME", "STACK_REGION")

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
    result = conn.get_template(stack_name)
    return result['GetTemplateResponse']['GetTemplateResult']['TemplateBody']

def diff_local_and_remote(data_file):
    data_json, local = escape_template(data_file, write=False)
    local = json_clean(local)
    remote = fetch_stack_template(
        data_json["STACK_NAME"], data_json["STACK_REGION"])
    remote = json_clean(remote)
    diff = difflib.unified_diff(
        remote.split("\n"), local.split("\n"), "REMOTE", "LOCAL")
    print("\n".join(diff))

def json_clean(json_str):
    json_data = json.loads(json_str)
    return json.dumps(
        json_data, indent=4, separators=(":", ","), sort_keys=True)

def json_load(path):
    check_file_exists(path)
    try:
        with open(path) as file_handle:
            return json.load(file_handle)
    except Exception as ex:
        print("Error loading {0} as JSON, please verify that "
            "it is valid JSON".format(path))
        print(ex)
        exit(1)

def check_file_exists(path):
    if not os.path.isfile(path):
        print("Error:  {0} does not exist".format(path))
        exit(1)

def read_file_text(path):
    check_file_exists(path)
    with open(path) as file_handle:
        return file_handle.read()

def write_file_text(path, text):
    with open(os.path.join(ORIG_WD, path), "w") as file_handle:
        file_handle.write(text)

def validate_data_file(path, validate=True):
    json_data = json_load(path)

    # All paths should be relative to the data file
    cwd = os.path.dirname(os.path.abspath(path))
    os.chdir(cwd)

    if "IMPORT" in json_data:
        import_list = json_data.pop("IMPORT")
        if not isinstance(import_list, list):
            print('ERROR:  "IMPORT" must be a list of '
                'strings:  ["file1", "file2", ...]')
            exit(1)
        import_dict = {}
        for path in import_list:
            import_data = validate_data_file(path, validate=False)
            for k, v in import_data.items():
                import_dict[k] = v
        # Override any inherited key/values with explicit values in the
        # current data file
        for k, v in json_data.items():
            import_dict[k] = v
        json_data = import_dict

    if not validate:
        return json_data

    result = [x for x in REQUIRED_TAGS
        if x not in json_data or not json_data[x].strip()]
    if result:
        print("Error:  {0} is missing required tags {1}".format(path, result))
        exit(1)
    for k in (k for k, v in json_data.items() if not v.strip()):
        print("WARNING:  Key '{0}' is an empty string".format(k))

    return json_data

def show_data_file(path):
    json_data = validate_data_file(path)
    result = json.dumps(
        json_data, indent=4, sort_keys=True)
    print(result)

def extract_tags_from_template(path):
    text = read_file_text(path)
    result = re.findall('{{\s*[a-zA-Z_-]+\s*}}', text)
    return set(x.strip("{} ") for x in result)

def generate_data_file_from_template(path, outfile):
    tags = extract_tags_from_template(path)
    result = collections.OrderedDict()
    for tag in REQUIRED_TAGS:
        result[tag] = path if tag == "CF_TEMPLATE" else ""
    for tag in sorted(tags):
        result[tag] = ""
    text = json.dumps(result, indent=4)
    write_file_text(outfile, text)

def escape_template(data_file, write=True):
    data_json = validate_data_file(data_file)
    cf_template = data_json["CF_TEMPLATE"]
    tags = extract_tags_from_template(cf_template)
    missing_tags = [x for x in tags if x not in data_json]
    if missing_tags:
        print("Error: {0} has missing "
            "tags {1}".format(data_file, missing_tags))
        exit(1)
    cf_text = read_file_text(cf_template)
    result = pystache.render(cf_text, data_json)
    if write:
        outfile = "{0}.json".format(data_json["STACK_NAME"])
        write_file_text(outfile, result)
        print("Created {0}".format(outfile))
    else:
        return data_json, result

def update_stack(data_file, create=False, print_status=False):
    data_json, result = escape_template(data_file, write=False)
    stack_region = data_json["STACK_REGION"]
    stack_name = data_json["STACK_NAME"]
    conn = get_cf_conn(stack_region)
    if create:
        try:
            conn.create_stack(stack_name, result)
        except boto.exception.BotoServerError:
            print("Error:  The requested stack already exists, use --update")
            exit(1)
    else:
        try:
            conn.update_stack(stack_name, result)
        except boto.exception.BotoServerError as ex:
            print("Unexpected error:\n")
            print(ex.message)
            exit(1)
    if print_status:
        wait(conn, stack_name)
    else:
        print("Stack operation started for {0}/{1}, you can monitor it's "
            "progress in the AWS web console".format(stack_region, stack_name))

def print_stack_event(event):
    print(" ".join(str(x) for x in (
        event.timestamp.isoformat(),
        event.resource_status,
        event.resource_type,
        event.logical_resource_id,
        event.physical_resource_id,
        event.resource_status_reason,
        "\n"
    )))

def wait(conn, stack_name):
    stack = conn.describe_stacks(stack_name)[0]
    events = list(conn.describe_stack_events(stack_name))
    seen_events = set((x.timestamp, x.logical_resource_id) for x in events)

    print("Last 3 events:\n")
    for event in events[:3]:
        print_stack_event(event)

    status = str(stack.stack_status)
    print("New events:\n")
    while not [x for x in ("COMPLETE", "FAILED") if x in status and
    not "PROGRESS" in status]:
        new_events = list(conn.describe_stack_events(stack_name))
        events_to_log = []
        for event in new_events:
            id_tuple = (event.timestamp, event.logical_resource_id)
            if id_tuple not in seen_events:
                seen_events.add(id_tuple)
                events_to_log.append(event)
        for event in reversed(events_to_log):
            print_stack_event(event)
        stack.update()
        status = str(stack.stack_status)
        time.sleep(5)
    print("{0}\n".format(status))
    if "FAIL" in status:
        exit(1)
    elif "COMPLETE" in status:
        exit(0)
    else:
        exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="Tool for managing AWS Cloudformation stacks using "
        "Mustache {{ tags }} to dynamically substitute values.  "
        "See https://github.com/j3ffhubb/simplecf for documentation and "
        "examples.")
    parser.add_argument(
        "-d", "--data-file", dest="data_file",
        help="This specifies the JSON data file containing the "
        "stack definition")
    me_group = parser.add_mutually_exclusive_group()
    me_group.add_argument(
        "-c", "--create-data-file", dest="template",
        help="Generate an empty data file from the tags in an "
        "existing template.  Specify -d for the output file name.")
    me_group.add_argument(
        "--show", dest="show", action="store_true",
        help="Perform all IMPORT's in --data-file and print the "
        "resulting key/value pairs")
    me_group.add_argument(
        "--diff", dest="diff", action="store_true",
        help="Print the unified diff of the local template vs. the "
        "template that was used to create the current version of "
        "the stack")
    me_group.add_argument(
        "--update", dest="update", action="store_true",
        help="Directly update the Cloudformation stack associated with -d")
    me_group.add_argument(
        "--create", dest="create", action="store_true",
        help="Directly create the Cloudformation stack associated with -d")
    parser.add_argument(
        "-w", "--wait", dest="wait", action="store_true",
        help="Wait for the --create or --update operation to finish "
        "before exiting, and print the stack events to stdout as they happen")
    parser.add_argument(
        "--version", dest="version", action="store_true",
        help="Show the application's version number")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)

    if not args.data_file:
        print("Error:  Must specify -d")
        exit(1)

    if args.template:
        generate_data_file_from_template(args.template, args.data_file)
    elif args.diff:
        diff_local_and_remote(args.data_file)
    elif args.show:
        show_data_file(args.data_file)
    elif args.update:
        update_stack(args.data_file, print_status=args.wait)
    elif args.create:
        update_stack(args.data_file, create=True, print_status=args.wait)
    else:
        escape_template(args.data_file)

if __name__ == "__main__":
    main()
