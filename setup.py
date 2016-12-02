from distutils.core import setup

import os
import imp

version_file = os.path.abspath("pyblish_bumpybox/version.py")
version_mod = imp.load_source("version", version_file)
version = version_mod.version

setup(
    name='pyblish-bumpybox',
    version=version,
    packages=['pyblish_bumpybox'],
    license="LGPL",
    long_description=open('README.md').read(),
)
