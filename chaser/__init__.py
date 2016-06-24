__version__ = "0.9.5"

import argparse
import gettext

gettext.bindtextdomain('chaser', '/usr/share/locale')
gettext.install('chaser', '/usr/share/locale')
gettext.textdomain('chaser')
_ = gettext.gettext

from chaser import chaser

def main(arguments=None):
    parser = argparse.ArgumentParser(
            description=_("Next-generation community package management for Chakra.")
    )
    subparsers = parser.add_subparsers()

    parser.add_argument('-v', '--version',
            help=_("show version information and exit"),
            action='version', version='Chaser {v}'.format(v=__version__)
    )

    parser.add_argument('-b', '--build-dir', metavar='BUILD_DIR',
            help=_("build packages in BUILD_DIR. default = ") + chaser.BUILD_DIR,
    )

    parser_g = subparsers.add_parser('get', help=_("download source files here"))
    parser_g.add_argument('package', nargs='+')
    parser_g.set_defaults(func=chaser.get_source_files, build_dir='.')

    parser_i = subparsers.add_parser('install', help=_("install a package from the CCR"))
    parser_i.add_argument('package', nargs='+')
    parser_i.set_defaults(func=chaser.install)

    parser_l = subparsers.add_parser('listupdates', help=_("list available updates"))
    parser_l.set_defaults(func=chaser.list_updates)

    parser_u = subparsers.add_parser('update', help=_("search for and install updates for CCR packages"))
    parser_u.set_defaults(func=chaser.update)

    parser_s = subparsers.add_parser('search', help=_("search CCR packages"))
    parser_s.add_argument('query')
    parser_s.set_defaults(func=chaser.search)

    parser_n = subparsers.add_parser('info', help=_("display package information"))
    parser_n.add_argument('package')
    parser_n.set_defaults(func=chaser.info)

    args = parser.parse_args(arguments)
    try:
        return args.func(args)
    except AttributeError:
        return parser.print_usage()
    except KeyboardInterrupt:
        return 1
