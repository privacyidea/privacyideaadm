# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
from setuptools.command.install import install
import os
import sys

version = "3.0"
name = 'privacyideaadm'
release = '3.0'

# Taken from kennethreitz/requests/setup.py
package_directory = os.path.realpath(os.path.dirname(__file__))


class InstallWithDoc(install):
    def run(self):
        self.run_command('build_sphinx')
        install.run(self)


cmdclass = {'install': InstallWithDoc}


def get_file_contents(file_path):
    """Get the context of the file using full path name."""
    content = ""
    try:
        full_path = os.path.join(package_directory, file_path)
        content = open(full_path, 'r').read()
    except:
        print("### could not open file {0!r}".format(file_path), file=sys.stderr)
    return content


setup(name=name,
      version=version,
      description='privacyIDEA admin Client',
      author='Cornelius Kölbel',
      author_email='cornelius@privacyidea.org',
      url='http://www.privacyidea.org',
      packages=['privacyideautils',
                'privacyideautils.commands'],
      setup_requires=['sphinx <= 1.8.5;python_version<"3.0"',
                      'sphinx >= 2.0;python_version>="3.0"'],
      install_requires=[
          "cffi",
          "click",
          "cryptography",
          "python-yubico",
          "qrcode",
          "requests",
          "six"
      ],
      cmdclass=cmdclass,
      command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'source_dir': ('setup.py', 'doc'),
            'build_dir': ('setup.py', os.path.join('doc', '_build')),
            'builder': ('setup.py', 'man')
        }
      },
      scripts=['scripts/privacyidea',
               'scripts/privacyidea-luks-assign',
               'scripts/privacyidea-authorizedkeys',
               'scripts/privacyidea-check-offline-otp',
               'scripts/privacyidea-get-offline-otp',
               'scripts/privacyidea-validate',
               'scripts/privacyidea-enroll-yubikey-piv'],
      data_files=[('share/man/man1', ["doc/_build/man/privacyidea.1"])],
      license='AGPLv3',
      long_description=get_file_contents('DESCRIPTION')
      )
