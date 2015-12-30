__version__ = "0.1"

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

    args = parser.parse_args()
    args.func(args.package)
