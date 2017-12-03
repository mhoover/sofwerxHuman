#!/usr/bin/python
import argparse
import json


def load_data(file):
    date = file.split('_')[1][:-5]

    with open(file, 'r') as f:
        tmp = json.load(f)
    res = {k: {date: v} for k, v in tmp.items()}

    return res

def merge(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def run(args_dict):
    data = [load_data(file) for file in args_dict['data']]

    result = merge(data[0], data[1])
    if len(data)>2:
        for d in data[2:]:
            result = merge(result, d)

    with open(args_dict['output'], 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine JSONs into one.')
    parser.add_argument('-d', '--data', required=True, nargs='*', help='JSONs '
                        'to combine.')
    parser.add_argument('-o', '--output', required=True, help='Name of output '
                        'file for data.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
