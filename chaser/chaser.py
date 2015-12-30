import io
import tarfile
import subprocess
import json
import re

import requests
from toposort import toposort_flatten
import ccr

from chaser import pacman

def get_source_files(pkgname, workingdir):
    """Download the source tarball and extract it"""
    r = requests.get(ccr.getpkgurl(pkgname))
    tar = tarfile.open(mode='r', fileobj=io.BytesIO(r.content))
    tar.extractall(workingdir)

def recurse_depends(pkgname, graph=None):
    if graph is None:
        graph = {}

    if graph.get(pkgname) is not None:
        # End case: already traversed
        return graph
    elif pacman.exists(pkgname):
        # End case: exists in pacman
        graph[pkgname] = set()
        return graph

    # Otherwise get dependencies
    graph[pkgname] = set()
    get_source_files(pkgname, ".")
    output = subprocess.check_output(["pkgvars.sh",
        "./{pkgname}/PKGBUILD".format(pkgname=pkgname)])
    data = json.loads(output.decode())['variables']
    # NOTE: We don't differentiate make/depends here, this is an area for
    # improvement in the future if someone cares.
    depends = data.get('makedepends', []) + data.get('depends', [])
    # Only depends that are not already installed
    for dep in depends:
        depname = re.split('[>=<]', dep)[0]
        if not pacman.is_installed(depname):
            graph[pkgname].add(depname)

    for dep in graph[pkgname]:
        recurse_depends(dep, graph)

    return graph

def dependency_chain(pkgname):
    """Return an ordered list of dependencies for a package"""
    depends = recurse_depends(pkgname)
    return toposort_flatten(depends)
