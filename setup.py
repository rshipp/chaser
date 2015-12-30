import os
from setuptools import setup

from chaser import __version__

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='chaser',
    version=__version__,
    packages=['chaser'],
    scripts=['pkgvars.sh', 'pkgvars.py'],
    entry_points = {
        'console_scripts': ['chaser = chaser:main'],
    },
    include_package_data=True,
    install_requires=[],
    license='BSD',
    description='Community package management for Chakra.',
    long_description=README,
    url='https://github.com/rshipp/chaser',
    author='Ryan Shipp',
    author_email='python@rshipp.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Software Distribution',
    ],
)
