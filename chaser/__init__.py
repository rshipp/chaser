__version__ = "0.6"

import argparse

from chaser import chaser

def main():
    parser = argparse.ArgumentParser(
            description="Next-generation community package management for Chakra."
    )
    subparsers = parser.add_subparsers()

    parser.add_argument('-v', '--version', 
            help="show version information and exit",
            action='version', version='Chaser {v}'.format(v=__version__)
    )

    parser_g = subparsers.add_parser('get', help="download source files here")
    parser_g.add_argument('package')
    parser_g.set_defaults(func=chaser.get_source_files)

    parser_i = subparsers.add_parser('install', help="install a package from the CCR")
    parser_i.add_argument('package')
    parser_i.set_defaults(func=chaser.install)

    parser_l = subparsers.add_parser('listupdates', help="list available updates")
    parser_l.set_defaults(func=chaser.list_updates)

    parser_u = subparsers.add_parser('update', help="search for and install updates for CCR packages")
    parser_u.set_defaults(func=chaser.update)

    parser_s = subparsers.add_parser('search', help="search CCR packages")
    parser_s.add_argument('query')
    parser_s.set_defaults(func=chaser.search)

    parser_n = subparsers.add_parser('info', help="display package information")
    parser_n.add_argument('package')
    parser_n.set_defaults(func=chaser.info)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
