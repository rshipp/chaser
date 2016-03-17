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

from chaser import pacman, prompt

BUILD_DIR = "/tmp/chaser"

def get_source_files(args, workingdir=None):
    """Download the source tarball and extract it, workingdir defaults to BUILD_DIR"""
    try:
        pkgname = args.package
        workingdir = args.build_dir or BUILD_DIR
    except AttributeError:
        pkgname = args
        workingdir = workingdir or BUILD_DIR

    if not os.path.exists(workingdir):
        os.mkdir(workingdir)

    r = requests.get(ccr.pkg_url(pkgname))
    r.raise_for_status()
    tar = tarfile.open(mode='r', fileobj=io.BytesIO(r.content))
    tar.extractall(workingdir)

def recurse_depends(pkgname, workingdir=None, graph=None):
    """Build a dependency graph"""
    if workingdir is None:
        workingdir = BUILD_DIR
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
    try:
        get_source_files(pkgname, workingdir)
    except requests.exceptions.HTTPError:
        # Package not found, or other error
        return graph
    output = subprocess.check_output(["pkgvars.sh",
        "{d}/{pkgname}/PKGBUILD".format(d=workingdir, pkgname=pkgname)])
    data = json.loads(output.decode())['variables']
    # NOTE: We don't differentiate make/depends here, this is an area for
    # improvement in the future if someone cares.
    depends = data.get('makedepends', []) + data.get('depends', [])
    # Only depends that are not already installed
    for dep in depends:
        depname = re.split('[>=<]', dep)[0]
        if not pacman.exists(depname):
            graph[pkgname].add(depname)

    for dep in graph[pkgname]:
        recurse_depends(dep, workingdir, graph)

    return graph

def dependency_chain(pkgname, workingdir=None):
    """Return an ordered list of dependencies for a package"""
    depends = recurse_depends(pkgname, workingdir)
    return toposort_flatten(depends)

def install(args):
    """Install a given package"""
    try:
        pkgname = args.package
        workingdir = args.build_dir or BUILD_DIR
    except AttributeError:
        pkgname = args
        workingdir = BUILD_DIR

    editor = os.getenv('EDITOR') or 'vim'
    try:
        # Make sure the package exists
        ccr.info(pkgname)
    except ccr.PackageNotFound:
        print(_("Package not found: {pkg}").format(pkg=pkgname))
        return 1

    print(_("Targets: {packages}").format(packages=' '.join(packages)))
    response = prompt.prompt(_("Proceed with installation?"))
    if response == prompt.NO:
        return 0
    for package in packages:
        try:
            get_source_files(package, workingdir)
        except (requests.exceptions.HTTPError, tarfile.ReadError):
            print("Package not found: {pkg}".format(pkg=package))
            return 1
        # Ask to edit the PKGBUILD
        response = prompt.prompt(_("Edit {pkg} PKGBUILD with $EDITOR?").format(pkg=package))
        if response == prompt.YES:
            subprocess.call([editor, "{d}/{pkg}/PKGBUILD".format(d=workingdir, pkg=package)])
        # Ask to edit the .install, if it exists
        if os.path.isfile("{d}/{pkg}/{pkg}.install".format(d=workingdir, pkg=package)):
            response = prompt.prompt(_("Edit {pkg}.install with $EDITOR?").format(pkg=package))
            if response == prompt.YES:
                subprocess.call([editor, "{d}/{pkg}/{pkg}.install".format(d=workingdir, pkg=package)])
        # makepkg
        curdir = os.getcwd()
        os.chdir(os.path.join(workingdir, package))
        subprocess.call(["makepkg", "-si"])
        os.chdir(curdir)

def check_updates(args=None):
    """Return list of (name, ver) tuples for packages with updates available"""
    installed = pacman.list_unofficial()
    updates = []
    for pkg in installed:
        pkgname, curver = pkg
        try:
            data = ccr.info(pkgname)
        except ccr.PackageNotFound:
            continue
        newver = data.get('Version', '0-0')
        if parse_version(newver) > parse_version(curver):
            updates.append((pkgname, newver))

    return updates

def list_updates(args=None):
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

    repo_results = pacman.search(query)
    if repo_results:
        for line in repo_results:
            print(line)

    results = ccr.search(query)
    if results == "No results found":
        return

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
    except ccr.PackageNotFound:
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
