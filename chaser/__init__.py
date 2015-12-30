__version__ = "0.3"

import argparse

from chaser import chaser

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_g = subparsers.add_parser('get')
    parser_g.add_argument('package')
    parser_g.set_defaults(func=chaser.get_source_files)

    parser_i = subparsers.add_parser('install')
    parser_i.add_argument('package')
    parser_i.set_defaults(func=chaser.install)

    parser_u = subparsers.add_parser('listupdates')
    parser_u.set_defaults(func=chaser.list_updates)

    parser_u = subparsers.add_parser('update')
    parser_u.set_defaults(func=chaser.update)

    args = parser.parse_args()
    try:
        args.func(args.package)
    except AttributeError:
        args.func()
