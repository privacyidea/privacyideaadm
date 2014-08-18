# -*- coding: utf-8 -*-
from distutils.core import setup
import os
import sys

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
      version='1.3',
      description='privacyIDEA admin Client',
      author='Cornelius Kölbel',
      author_email='cornelius@privacyidea.org',
      url='http://www.privacyidea.org',
      packages=['privacyideautils'],
      scripts=['privacyideaadm',
               'privacyidea',
               'privacyidea-luks-assign',
               'privacyidea-ssh-assign'],
      install_requires=['usb'],
      data_files=[('share/man/man1', ["privacyideaadm.1",
                                      "doc/_build/man/privacyidea.1"])],
      license='AGPLv3',
      long_description=get_file_contents('DESCRIPTION')
      )
