import io
import tarfile
import subprocess
import json
import re
import os

from pkg_resources import parse_version
import requests
from toposort import toposort_flatten
import ccr

from chaser import pacman, prompt, config

BUILD_DIR = os.path.expanduser(config.get('BuildDir'))

def get_source_files(args, workingdir=None):
    """Download the source tarball and extract it, workingdir defaults to BUILD_DIR"""
    try:
        pkgname = args.package
        workingdir = "."
    except AttributeError:
        pkgname = args
        workingdir = workingdir or BUILD_DIR

    if not os.path.exists(workingdir):
        os.mkdir(workingdir)

    r = requests.get(ccr.getpkgurl(pkgname))
    tar = tarfile.open(mode='r', fileobj=io.BytesIO(r.content))
    tar.extractall(workingdir)

def recurse_depends(pkgname, graph=None):
    """Build a dependency graph"""
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
    get_source_files(pkgname)
    output = subprocess.check_output(["pkgvars.sh",
        "{d}/{pkgname}/PKGBUILD".format(d=BUILD_DIR, pkgname=pkgname)])
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

def install(args):
    """Install a given package"""
    try:
        pkgname = args.package
    except AttributeError:
        pkgname = args

    editor = os.getenv('EDITOR')
    for package in dependency_chain(pkgname):
        try:
            get_source_files(package)
        except tarfile.ReadError:
            print("Package not found: {pkg}".format(pkg=package))
            return 1
        # Ask to edit the PKGBUILD
        response = prompt.prompt(_("Edit {pkg} PKGBUILD with $EDITOR?").format(pkg=package))
        if response == prompt.YES:
            subprocess.call([editor, "{d}/{pkg}/PKGBUILD".format(d=BUILD_DIR, pkg=package)])
        # Ask to edit the .install, if it exists
        if os.path.isfile("{d}/{pkg}/{pkg}.install".format(d=BUILD_DIR, pkg=package)):
            response = prompt.prompt(_("Edit {pkg}.install with $EDITOR?").format(pkg=package))
            if response == prompt.YES:
                subprocess.call([editor, "{d}/{pkg}/{pkg}.install".format(d=BUILD_DIR, pkg=package)])
        # makepkg -i
        curdir = os.getcwd()
        os.chdir(os.path.join(BUILD_DIR, pkgname))
        subprocess.call(["makepkg", "-i"])
        os.chdir(curdir)

def check_updates(args):
    """Return list of (name, ver) tuples for packages with updates available"""
    installed = pacman.list_unofficial()
    updates = []
    for pkg in installed:
        pkgname, curver = pkg
        try:
            data = ccr.info(pkgname)
        except ccr.ccr.PackageNotFound:
            continue
        newver = data.get('Version', '0-0')
        if parse_version(newver) > parse_version(curver):
            updates.append((pkgname, newver))

    return updates

def list_updates(args):
    """List currently installed unofficial packages in `name ver` format"""
    for name, ver in check_updates():
        print(name, ver)

def update(args):
    """Install updates"""
    updates = check_updates()
    print(_("Updates: {pkgs}").format(pkgs='  '.join([ '-'.join(p) for p in updates ])))
    response = prompt.prompt(_("Continue with installation?"))
    if response == prompt.YES:
        for name, ver in updates:
            install(name)

def search(args):
    """Print search results"""
    try:
        query = args.query
    except AttributeError:
        query = args

    results = ccr.search(query)
    results.sort(key=lambda x: x.Name)
    for pkg in results:
        print("ccr/{name} {ver}".format(name=pkg.Name, ver=pkg.Version))
        print("    {desc}".format(desc=pkg.Description))

def info(args):
    """Print package info"""
    try:
        package = args.package
    except AttributeError:
        package = args

    try:
        results = ccr.info(package)
    except ccr.ccr.PackageNotFound:
        print("Package not found")
        return 1

    print(_("Name           : {name}").format(name=results.Name))
    print(_("Version        : {ver}").format(ver=results.Version))
    print(_("URL            : {url}").format(url=results.URL))
    print(_("Licenses       : {license}").format(license=results.License))
    print(_("Category       : {cat}").format(cat=results.Category))
    print(_("Votes          : {votes}").format(votes=results.NumVotes))
    print(_("Maintainer     : {name}").format(name=results.Maintainer))
    print(_("OutOfDate      : {val}").format(val=True if results.OutOfDate == '1' else False))
    print(_("Description    : {desc}").format(desc=results.Description))
