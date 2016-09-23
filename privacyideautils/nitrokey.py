#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  privacyIDEA
#  2016-09-05 Cornelius Kölbel <corneluis.koelbel@netknights.it>
#             Use new libnitrokey and cffi
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

import os
import binascii
import cffi
from enum import Enum


class DeviceErrorCode(Enum):
    STATUS_OK = 0
    NOT_PROGRAMMED = 3
    WRONG_PASSWORD = 4
    STATUS_NOT_AUTHORIZED = 5
    STATUS_AES_DEC_FAILED = 0xa

CDefs = """
void NK_set_debug(bool state);
int NK_login(const char *device_model);
int NK_login_auto();
int NK_logout();
const char * NK_status();
uint8_t NK_get_last_command_status();
int NK_lock_device();
int NK_user_authenticate(const char* user_password, const char* user_temporary_password);
int NK_first_authenticate(const char* admin_password, const char* admin_temporary_password);
int NK_factory_reset(const char* admin_password);
int NK_build_aes_key(const char* admin_password);
int NK_unlock_user_password(const char *admin_password, const char *new_user_password);
int NK_write_config(uint8_t numlock, uint8_t capslock, uint8_t scrolllock,bool enable_user_password, bool delete_user_password, const char *admin_temporary_password);
uint8_t* NK_read_config();
const char * NK_get_totp_slot_name(uint8_t slot_number);
const char * NK_get_hotp_slot_name(uint8_t slot_number);
int NK_erase_hotp_slot(uint8_t slot_number, const char *temporary_password);
int NK_erase_totp_slot(uint8_t slot_number, const char *temporary_password);
int NK_write_hotp_slot(uint8_t slot_number, const char *slot_name, const char *secret, uint8_t hotp_counter,bool use_8_digits, bool use_enter, bool use_tokenID, const char *token_ID,const char *temporary_password);
int NK_write_totp_slot(uint8_t slot_number, const char *slot_name, const char *secret, uint16_t time_window,bool use_8_digits, bool use_enter, bool use_tokenID, const char *token_ID,const char *temporary_password);
uint32_t NK_get_hotp_code(uint8_t slot_number);
uint32_t NK_get_hotp_code_PIN(uint8_t slot_number, const char* user_temporary_password);
uint32_t NK_get_totp_code(uint8_t slot_number, uint64_t challenge, uint64_t last_totp_time, uint8_t last_interval);
uint32_t NK_get_totp_code_PIN(uint8_t slot_number, uint64_t challenge,uint64_t last_totp_time, uint8_t last_interval, const char* user_temporary_password);
int NK_totp_set_time(uint64_t time);
int NK_totp_get_time();
int NK_change_admin_PIN(char *current_PIN, char *new_PIN);
int NK_change_user_PIN(char *current_PIN, char *new_PIN);
uint8_t NK_get_user_retry_count();
uint8_t NK_get_admin_retry_count();
int NK_enable_password_safe(const char *user_pin);
uint8_t * NK_get_password_safe_slot_status();
const char *NK_get_password_safe_slot_name(uint8_t slot_number);
const char *NK_get_password_safe_slot_login(uint8_t slot_number);
const char *NK_get_password_safe_slot_password(uint8_t slot_number);
int NK_write_password_safe_slot(uint8_t slot_number, const char *slot_name,const char *slot_login, const char *slot_password);
int NK_erase_password_safe_slot(uint8_t slot_number);
int NK_is_AES_supported(const char *user_password);
"""


class NitroKey(object):

    def __init__(self):
        self.ffi = cffi.FFI()
        for declaration in CDefs.split("\n"):
            self.ffi.cdef(declaration)
        self.nitrokey = self.ffi.dlopen("libnitrokey.so")
        self.session_password = None

    def admin_login(self, password):
        device_connected = self.nitrokey.NK_login_auto()
        if device_connected == 1:
            r = self.nitrokey.NK_set_debug(False)
            self.session_password = binascii.hexlify(os.urandom(8))
            r = self.nitrokey.NK_first_authenticate(password,
                                                    self.session_password)
            if r != 0:
                raise Exception("Failed to login. {0!s}".format(r))
        else:
            raise Exception("No Nitrokey connected. {0!s}".format(device_connected))

    def init_hotp(self, slot, slotname, otp_key=None,
                  digits=6):
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
        :param digits: Number of OTP digits 6 or 8 allowed.
        :return: the otp key
        """
        if not self.session_password:
            raise Exception("You need to login as admin first!")
        if not 0 <= slot <= 2:
            raise Exception("Only HOTP slots between 0 and 2 are allowed.")
        use_8_digits = digits == 8
        if not otp_key:
            otp_key = os.urandom(10)
            otp_key_hex = binascii.hexlify(otp_key)
        else:
            otp_key_hex = otp_key

        r = self.nitrokey.NK_erase_hotp_slot(slot,
                                             self.session_password)
        if r != 0:
            #raise Exception("Error deleting OTP slot. {0!s}".format(r))
            print("Error deleting OTP slot. {0!s}".format(r))
        r = self.nitrokey.NK_write_hotp_slot(slot, slotname, otp_key, 0,
                                             use_8_digits, False, False, "",
                                             self.session_password)
        if r != 0:
            raise Exception("Error writing OTP slot. {0!s}".format(r))

        return otp_key_hex

    def logout(self):
        r = self.nitrokey.NK_logout()

    def status(self):
        """
        NK_status returns a cdata which can be transformed to this string:
        firmware_version:	7
        card_serial:	0000	a7 23 00 00
        general_config:	0000	01 00 ff 00 00
        numlock:	1
        capslock:	0
        scrolllock:	255
        enable_user_password:	0
        delete_user_password:	0
        :return:
        """
        r = self.nitrokey.NK_status()
        s = self.ffi.string(r)
        ret = {}
        for line in s.split("\n"):
            if ":" in line:
                key, val = line.split(":")
                if key:
                    ret[key] = val.strip()

        return ret


if __name__ == "__main__":
    Nk = NitroKey()
    Nk.admin_login("12345678")
    otp_key = Nk.init_hotp(2, "privadyidea")
    print otp_key
    print Nk.status()
    Nk.logout()
