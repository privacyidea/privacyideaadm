#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  privacyIDEA
#  2016-04-30 Cornelius Kölbel, <cornelius@privacyidea.org>
#             initial writeup
#
#  (c) 2016 Cornelius Kölbel, cornelius@privacyidea.org
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from ctypes import CDLL, RTLD_GLOBAL
from ctypes.util import find_library
import os
import binascii


class NitroKey(object):

    def __init__(self):
        libs = ["libusb-1.0.so", "linux-vdso.so.1", "libhidapi-libusb.so.0",
                "libstdc++.so.6", "libm.so.6", "libgcc_s.so.1",
                "libc.so.6", "librt.so.1", "libpthread.so.0", "libudev.so.1",
                "libcgmanager.so.0", "libnih.so.1",
                "libdbus-1.so.3"]
        for l in libs:
            CDLL(l, mode = RTLD_GLOBAL)
        lib = find_library("nitrokey")
        print("Using library %s" % lib)
        self.nitrokey = CDLL(lib, mode = RTLD_GLOBAL)

    def init_hotp(self, slot, password, slotname, otp_key=None):
        """
        Initilize the given slot with an HOTP key.

        If otp_key is not specified, then a random key is generated and
        returned.

        :param slot: The slot number, 15-17
        :type slot: int
        :param password: The card password
        :type password: basestring
        :param slotname: The new name of the slot
        :type slotname: basestring
        :param otp_key: The OTP secret key
        :type slotname: A hexstring
        :return: the otp key
        """
        if not otp_key:
            otp_key = binascii.hexlify(os.urandom(20))
        self.nitrokey.initHotp(slot, password, otp_key, slotname)
        return otp_key


if __name__ == "__main__":
    Nk = NitroKey()
    otp_key = Nk.init_hotp(15, "12345678", "pi")
    print otp_key
