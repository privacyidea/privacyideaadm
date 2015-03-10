privacyideaadm
==============

This is a command line client to manage the privacyIDEA server.

You can use it to fill an LUKS keyslot with the response
of a challenge response Yubikey, that is managed with
privacyIDEA.

.note:: You will also need the package at https://github.com/cornelinux/yubikey-luks to enable
   grub to read challenges from the yubikey.

You can also use it to manage SSH keys centrally for all your
servers running openssh.
