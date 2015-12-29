__version__ = "0.1"

import requests
import io
import tarfile

import ccr

def get_source_files(pkgname, workingdir):
    """Download the source tarball and extract it"""
    r = requests.get(ccr.getpkgurl(pkgname))
    tar = tarfile.open(mode='r', fileobj=io.BytesIO(r.content))
    tar.extractall(workingdir)
