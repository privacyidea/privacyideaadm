privacyideaadm
==============

This is a command line client to manage the privacyIDEA server.

Usage
-----

Use `privacyidea --help` or `privacyidea <COMMAND> --help` respectively to
display available commands and options.

Installation
------------
Using a python virtualenv a simple `pip install .` should suffice to make
the admin tool available.<br/>
Note that the extra tools might require additional (python) packages.

Additional Tools
----------------

The `scripts` folder contains tools for additional functionality

### privacyidea-enroll-yubikey-piv:
Enroll a Certificate Token using the YubiKey PIV application.
This requires a working CA configuration in privacyIDEA.

> **Warning:**<br/>
> This tool is still work in progress and should not be used for security
> sensitive operations

### privacyidea-luks-assign:
You can use it to fill an LUKS keyslot with the response
of a challenge response Yubikey, that is managed with
privacyIDEA.

> **Note:**<br/>
> You will also need the package at https://github.com/cornelinux/yubikey-luks to enable
> grub to read challenges from the yubikey.

You can also use it to manage SSH keys centrally for all your
servers running openssh.
