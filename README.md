privacyideaadm
==============

This is a command line client to manage the privacyIDEA server.

You can now use it to fill a LUKS keyslot with the response
of a challenge response Yubikey, that is managed with
privacyIDEA 1.2+

   ./privacyidea-luks-assign -U https://172.16.200.139:5001 --admin=admin@admin --name=2ndclient --clearslot

.note:: You will also need the package at https://github.com/cornelinux/yubikey-luks to enable
   grub to read challenges from the yubikey.
