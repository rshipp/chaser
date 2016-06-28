import os
import glob
import shutil
from setuptools import setup
from setuptools.command.install import install

from chaser import __version__

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

class Install(install):
    def run(self):
        install.run(self)
        # Install locales
        if self.root:
            usr_dir = "%s/usr" % self.root
        else:
            usr_dir = "/usr"
        locale_dir = os.path.join(usr_dir, "share/locale")

        print("Installing locales...")
        for filename in glob.glob1("po", "*.po"):
            lang = filename.rsplit(".", 1)[0]
            os.system("msgfmt po/%s.po -o po/%s.mo" % (lang, lang))
            try:
                os.makedirs(os.path.join(locale_dir, "%s/LC_MESSAGES" % lang))
            except OSError:
                pass
            shutil.copy("po/%s.mo" % lang, os.path.join(locale_dir, "%s/LC_MESSAGES" % lang, "%s.mo" % "chaser"))


setup(
    name='chaser',
    version=__version__,
    packages=['chaser'],
    scripts=['pkgvars.sh', 'pkgvars.py'],
    entry_points = {
        'console_scripts': ['chaser = chaser:main',
                            'pchaser = chaser.pchaser:main'],
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
    cmdclass={
        'install': Install,
    },
)
