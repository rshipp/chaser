import os
import configparser

CONFDIR = os.path.expanduser("~/.config/")
CONFIG = os.path.join(CONFDIR, "chaserrc")

def create():
    if not os.path.isdir(CONFDIR):
        os.mkdir(CONFDIR)
    with open(CONFIG, "w+") as f:
        f.write("[Options]\n")
        f.write("BuildDir = ~/ccr\n")

def get(option):
    if not os.path.isfile(CONFIG):
        create()
    parser = configparser.ConfigParser()
    parser.read(CONFIG)
    return parser.get('Options', option)
