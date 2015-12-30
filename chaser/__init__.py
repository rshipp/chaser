__version__ = "0.1"

import argparse

from chaser import chaser

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_i = subparsers.add_parser('install')
    parser_i.add_argument('package')
    parser_i.set_defaults(func=chaser.install)

    args = parser.parse_args()
    args.func(args.package)
