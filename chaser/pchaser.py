import sys

import chaser

def main():
    conversions = {
        '-S': 'install',
        '-Syu': 'update',
        '-Qu': 'listupdates',
        '-G': 'get',
        '-Ss': 'search',
        '-Si': 'info',
        '-Sii': 'info',
    }

    try:
        if sys.argv[1] in conversions:
            sys.argv[1] = conversions[sys.argv[1]]
    except IndexError:
        short_usage()
        exit(0)

    if '-h' in sys.argv or '--help' in sys.argv:
        usage()
        exit(0)

    chaser.main(sys.argv[1:])

def short_usage():
    print(_('usage: pchaser [-h] [-v] [-b BUILD_DIR]'))
    print(_('               {-G,-S,-Qu,-Syu,-Ss,-Si} ...'))

def usage():
    short_usage()
    print(_('Next-generation community package management for Chakra.'))
    print(_('(Pacman-style wrapper)'))
    print()
    print(_('positional arguments:'))
    print(_('  {-G,-S,-Qu,-Syu,-Ss,-Si}'))
    print(_('    -G                  download source files here'))
    print(_('    -S                  install a package from the CCR'))
    print(_('    -Qu                 list available updates'))
    print(_('    -Syu                search for and install updates for CCR packages'))
    print(_('    -Ss                 search CCR packages'))
    print(_('    -Si, -Sii           display package information'))
    print()
    print(_('optional arguments:'))
    print(_('  -h, --help            show this help message and exit'))
    print(_('  -v, --version         show version information and exit'))
    print(_('  -b BUILD_DIR, --build-dir BUILD_DIR'))
    print(_('                        build packages in BUILD_DIR. default = /tmp/chaser'))
