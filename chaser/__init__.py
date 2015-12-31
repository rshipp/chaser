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

    parser_l = subparsers.add_parser('listupdates')
    parser_l.set_defaults(func=chaser.list_updates)

    parser_u = subparsers.add_parser('update')
    parser_u.set_defaults(func=chaser.update)

    parser_s = subparsers.add_parser('search')
    parser_s.add_argument('query')
    parser_s.set_defaults(func=chaser.search)

    parser_n = subparsers.add_parser('info')
    parser_n.add_argument('package')
    parser_n.set_defaults(func=chaser.info)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print("No operation specified")
