# -*- coding: utf-8 -*-
from distutils.core import setup
import os
import sys

#VERSION="2.1dev4"
VERSION = "2.15.1"

# Taken from kennethreitz/requests/setup.py
package_directory = os.path.realpath(os.path.dirname(__file__))


def get_file_contents(file_path):
    """Get the context of the file using full path name."""
    content = ""
    try:
        full_path = os.path.join(package_directory, file_path)
        content = open(full_path, 'r').read()
    except:
        print >> sys.stderr, "### could not open file %r" % file_path
    return content


setup(name='privacyideaadm',
      version=VERSION,
      description='privacyIDEA admin Client',
      author='Cornelius Kölbel',
      author_email='cornelius@privacyidea.org',
      url='http://www.privacyidea.org',
      packages=['privacyideautils'],
      install_requires=["requests", "pysqlite"],
      scripts=['scripts/privacyidea',
               'scripts/privacyidea-luks-assign',
	           'scripts/privacyidea-authorizedkeys'],
#      install_requires=['usb'],
      data_files=[('share/man/man1', ["doc/_build/man/privacyidea.1"])],
      license='AGPLv3',
      long_description=get_file_contents('DESCRIPTION')
      )
