# -*- coding: utf-8 -*-
from __future__ import print_function
from distutils.core import setup
import os
import sys

VERSION = "2.22.1"

# Taken from kennethreitz/requests/setup.py
package_directory = os.path.realpath(os.path.dirname(__file__))


def get_file_contents(file_path):
    """Get the context of the file using full path name."""
    content = ""
    try:
        full_path = os.path.join(package_directory, file_path)
        content = open(full_path, 'r').read()
    except:
        print("### could not open file {0!r}".format(file_path), file=sys.stderr)
    return content


setup(name='privacyideaadm',
      version=VERSION,
      description='privacyIDEA admin Client',
      author='Cornelius Kölbel',
      author_email='cornelius@privacyidea.org',
      url='http://www.privacyidea.org',
      packages=['privacyideautils'],
      install_requires=["requests",
                        "qrcode",
                        "cffi",
                        "enum34"],
      scripts=['scripts/privacyidea',
               'scripts/privacyidea-luks-assign',
               'scripts/privacyidea-authorizedkeys'],
      data_files=[('share/man/man1', ["doc/_build/man/privacyidea.1"])],
      license='AGPLv3',
      long_description=get_file_contents('DESCRIPTION')
      )
