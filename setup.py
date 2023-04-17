# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    packages=['privacyideautils',
              'privacyideautils.commands'],
    scripts=[
        'scripts/privacyidea',
        'scripts/privacyidea-luks-assign',
        'scripts/privacyidea-authorizedkeys',
        'scripts/privacyidea-check-offline-otp',
        'scripts/privacyidea-get-offline-otp',
        'scripts/privacyidea-validate',
        'scripts/privacyidea-enroll-yubikey-piv'
    ]
)
