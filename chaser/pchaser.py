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
    print('usage: pchaser [-h] [-v] [-b BUILD_DIR]')
    print('               {-G,-S,-Qu,-Syu,-Ss,-Si} ...')

def usage():
    short_usage()
    print('Next-generation community package management for Chakra.')
    print('(Pacman-style wrapper)')
    print()
    print('positional arguments:')
    print('  {-G,-S,-Qu,-Syu,-Ss,-Si}')
    print('    -G                  download source files here')
    print('    -S                  install a package from the CCR')
    print('    -Qu                 list available updates')
    print('    -Syu                search for and install updates for CCR packages')
    print('    -Ss                 search CCR packages')
    print('    -Si, -Sii           display package information')
    print()
    print('optional arguments:')
    print('  -h, --help            show this help message and exit')
    print('  -v, --version         show version information and exit')
    print('  -b BUILD_DIR, --build-dir BUILD_DIR')
    print('                        build packages in BUILD_DIR. default = /tmp/chaser')
