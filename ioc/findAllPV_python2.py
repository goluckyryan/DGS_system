#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import os

def parse_dbloadrecords(startup_file):
    """
    Reads a file with dbLoadRecords() lines and returns a list of
    tuples: (template_file, {macro_name: value})
    """
    results = []
    pattern = re.compile(
        r'dbLoadRecords\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)'
    )

    with open(startup_file, 'r') as f:
        for line in f:
            match = pattern.search(line)
            print(match.group(1))
            if match:
                template_file = match.group(1)
                macro_str = match.group(2)
                macros = dict(item.split("=") for item in macro_str.split(","))
                results.append((template_file, macros))
    return results


def parse_template_with_macros(template_file, macros):
    """
    Reads a template file, extracts record names and performs macro substitution.
    Returns a list of (record_type, substituted_record_name, substituted_fields)
    """
    results = []
    record_pattern = re.compile(r'record\((\w+)\s*,\s*"([^"]+)"\)')
    field_pattern = re.compile(r'field\((\w+)\s*,\s*"([^"]+)"\)')

    with open(template_file, 'r') as f:
        content = f.read()

    for record_match in record_pattern.finditer(content):
        record_type = record_match.group(1)
        record_name = record_match.group(2)

        for k, v in macros.items():
            record_name = record_name.replace("$({})".format(k), v)

        # Extract block content
        start_idx = record_match.end()
        brace_level = 0
        block_lines = []
        inside_block = False
        for line in content[start_idx:].splitlines():
            if "{" in line:
                brace_level += 1
                inside_block = True
                continue
            if "}" in line:
                brace_level -= 1
                if brace_level <= 0:
                    break
            if inside_block:
                block_lines.append(line)

        substituted_fields = []
        for field_match in field_pattern.finditer("\n".join(block_lines)):
            field_name = field_match.group(1)
            field_value = field_match.group(2)
            for k, v in macros.items():
                field_value = field_value.replace("$({})".format(k), v)
            substituted_fields.append((field_name, field_value))

        results.append((record_type, record_name, substituted_fields))

    return results


def process_startup_and_templates(startup_file, base_dir):
    db_entries = parse_dbloadrecords(startup_file)
    all_results = []
    for template_file, macros in db_entries:
        template_path = os.path.join(base_dir, template_file)
        if not os.path.exists(template_path):
            print("Template file not found: {}".format(template_path))
            continue
        records = parse_template_with_macros(template_path, macros)
        all_results.extend(records)
    return all_results


if __name__ == "__main__":
    startup_path = "boot/vme32.trigger.cmd"  # file containing dbLoadRecords()
    base_dir = "."  # directory where db templates are stored

    print(startup_path)

    results = process_startup_and_templates(startup_path, base_dir)

    for rec_type, rec_name, fields in results:
        print("{}: {}".format(rec_type, rec_name))
        for fname, fval in fields:
            print("    {} = {}".format(fname, fval))
        print("")

