#!/usr/bin/env python

import json
import fileinput

def main():
    fileno = -1
    files = ['', '', '']
    for line in fileinput.input():
        if fileinput.filelineno() == 1:
            fileno += 1
        files[fileno] += line

    before = set(files[0].split('\x00'))
    after = set(files[1].split('\x00'))
    arrays = set(files[2].strip().split('\n'))

    print(to_json(before, after, arrays))

def to_json(before, after, arrays):
    """Returns a valid JSON string containing functions and variables.

    Parameters are three sets, in the format produced by ``pkgvars.sh`` and
    this module's main() function.
    """
    variables = {}
    functions = {}
    for line in after.difference(before):
        split_at = line.find('=')
        var = line[:split_at]
        value = line[split_at+1:]
        if value.startswith('() {'):
            functions[var[10:-2]] = [line.strip('\n; ') for line in value.strip('() {}\n').split('\n')]
        else:
            variables[var] = value.rstrip()
    for line in arrays:
        split_at = line.find('=')
        var = line[:split_at]
        value = line[split_at+1:]
        if value == '( )':
            continue
        value = [v.replace('\0', ' ').strip(' \'') for v in value.strip("'() \n").split(' ')]
        variables[var] = value

    return json.dumps({'variables': variables, 'functions': functions}, indent=4)

if __name__ == "__main__":
    main()
