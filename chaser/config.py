import os
import configparser

CONFIG = os.path.expanduser("~/.config/chaserrc")

def create():
    with open(CONFIG, "w+") as f:
        f.write("[Options]\n")
        f.write("BuildDir = ~/ccr\n")

def get(option):
    if not os.path.isfile(CONFIG):
        create()
    parser = configparser.ConfigParser()
    parser.read(CONFIG)
    return parser.get('Options', option)
