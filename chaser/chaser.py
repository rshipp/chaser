import io
import tarfile
import subprocess
import json
import re
import os

import termcolor
import progressbar
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
        if not pacman.exists(depname) and not pacman.is_installed(depname):
            graph[pkgname].add(depname)

    for dep in graph[pkgname]:
        recurse_depends(dep, workingdir, graph)

    return graph

def dependency_chain(pkgname, workingdir=None):
    """Return an ordered list of dependencies for a package"""
    depends = recurse_depends(pkgname, workingdir)
    return toposort_flatten(depends)

def print_targets(packages):
    """Formatted print"""
    print()
    print(termcolor.colored(_("Targets"), attrs=['bold']) + \
          termcolor.colored(" ({num}) ".format(num=len(packages)), attrs=['bold']) + \
          "{packages}".format(num=len(packages), packages='  '.join(['-'.join(p) for p in packages if type(p) == tuple] or packages)))
    print()

def install(args):
    """Install a given package"""
    try:
        pkgname = args.package
        workingdir = args.build_dir or BUILD_DIR
    except AttributeError:
        pkgname = args
        workingdir = BUILD_DIR

    print(_("resolving dependencies..."))

    editor = os.getenv('EDITOR') or 'vim'
    try:
        # Make sure the package exists
        ccr.info(pkgname)
    except ccr.PackageNotFound:
        print(_("Package not found: {pkg}").format(pkg=pkgname))
        return 1

    packages = dependency_chain(pkgname, workingdir)

    print_targets(packages)
    response = prompt.prompt(_("Proceed with installation?"), major=True)
    if response == prompt.NO:
        return 0
    for package in packages:
        try:
            get_source_files(package, workingdir)
        except (requests.exceptions.HTTPError, tarfile.ReadError):
            print(_("Package not found: {pkg}").format(pkg=package))
            return 1
        # Ask to edit the PKGBUILD
        response = prompt.prompt(_("Edit {pkg} PKGBUILD with $EDITOR?").format(pkg=package), color='yellow')
        if response == prompt.YES:
            subprocess.call([editor, "{d}/{pkg}/PKGBUILD".format(d=workingdir, pkg=package)])
        # Ask to edit the .install, if it exists
        if os.path.isfile("{d}/{pkg}/{pkg}.install".format(d=workingdir, pkg=package)):
            response = prompt.prompt(_("Edit {pkg}.install with $EDITOR?").format(pkg=package), color='yellow')
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
    with progressbar.ProgressBar(max_value=len(installed)) as bar:
        for i, pkg in enumerate(installed):
            pkgname, curver = pkg
            try:
                data = ccr.info(pkgname)
            except ccr.PackageNotFound:
                continue
            newver = data.get('Version', '0-0')
            if parse_version(newver) > parse_version(curver):
                updates.append((pkgname, newver))
            bar.update(i)

    return updates

def list_updates(args=None):
    """List currently installed unofficial packages in `name ver` format"""
    for name, ver in check_updates():
        print(name, ver)

def update(args):
    """Install updates"""
    print(termcolor.colored(":: ", 'blue', attrs=['bold']) + \
          termcolor.colored(_("Checking for updates..."), attrs=['bold']))
    updates = check_updates()
    print_targets(updates)
    response = prompt.prompt(_("Continue with installation?"), major=True)
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
        print(''.join([
            termcolor.colored("ccr/", color='magenta', attrs=['bold']),
            termcolor.colored(pkg.Name, attrs=['bold']), ' ',
            termcolor.colored(pkg.Version, color='green', attrs=['bold'])]))
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

    print(''.join([
        termcolor.colored(_("Name           : "), attrs=['bold']), results.Name, '\n',
        termcolor.colored(_("Version        : "), attrs=['bold']), results.Version, '\n',
        termcolor.colored(_("URL            : "), attrs=['bold']), results.URL, '\n',
        termcolor.colored(_("Licenses       : "), attrs=['bold']), results.License, '\n',
        termcolor.colored(_("Category       : "), attrs=['bold']), results.Category, '\n',
        termcolor.colored(_("Votes          : "), attrs=['bold']), str(results.NumVotes), '\n',
        termcolor.colored(_("Maintainer     : "), attrs=['bold']), results.Maintainer, '\n',
        termcolor.colored(_("OutOfDate      : "), attrs=['bold']), "{val}".format(val=True if results.OutOfDate == '1' else False), '\n',
        termcolor.colored(_("Description    : "), attrs=['bold']), results.Description,
    ]))
