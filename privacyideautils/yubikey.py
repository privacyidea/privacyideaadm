#!/usr/bin/python
# -*- coding: utf-8 -*-
#  privacyIDEA is a fork of LinOTP
#  May 08, 2014 Cornelius Kölbel
#  License:  AGPLv3
#  contact:  http://www.privacyidea.org
#
#  Copyright (C) 2010 - 2014 LSE Leading Security Experts GmbH
#  License:  AGPLv3
#  contact:  http://www.linotp.org
#            http://www.lsexperts.de
#            linotp@lsexperts.de
'''
This module is used for enrolling yubikey

'''
try:
    import yubico
    import yubico.yubikey
    import yubico.yubikey_defs
    from yubico.yubikey import YubiKeyError
    from usb import USBError
except ImportError as e:
    print("python yubikey module not available.")
    print("please get it from https://github.com/Yubico/python-yubico if you want to enroll yubikeys")
    print(str(e))
    
from time import sleep
import sys
import re
import os
import six
import binascii
import codecs
import string
try:
    maketrans = string.maketrans
except AttributeError:
    maketrans = bytes.maketrans

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("No cryptography package available. "
          "You can not enroll yubikeys with static password.")

MODE_YUBICO = "YUBICO"
MODE_OATH = "OATH"
MODE_STATIC = "STATIC"

hexHexChars = b'0123456789abcdef'
modHexChars = b'cbdefghijklnrtuv'

t_map = maketrans(hexHexChars, modHexChars)


def to_bytes(s):
    if isinstance(s, bytes):
        return s
    elif isinstance(s, six.text_type):
        return s.encode('utf8')
    return s


def modhex_encode(s):
    s = to_bytes(s)
    return binascii.hexlify(s).translate(t_map)


class YubiError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def create_static_password(key_hex):
    '''
    According to yubikey manual 5.5.5 the static-ticket is the same algorith with no moving factors.
    The msg_hex that is encoded with the aes key is '000000000000ffffffffffffffff0f2e'
    '''
    if not CRYPTO_AVAILABLE:
        raise Exception("No cryptography package available. "
                        "You can not enroll Yubikey with static password!")
    
    msg_hex = "000000000000ffffffffffffffff0f2e"
    msg_bin = binascii.unhexlify(msg_hex)
    backend = default_backend()
    cipher = Cipher(algorithms.AES(binascii.unhexlify(key_hex)), modes.ECB(),
                    backend=backend)
    encryptor = cipher.encryptor()
    password_bin = encryptor.update(msg_bin) + encryptor.finalize()
    password = modhex_encode(password_bin)
    
    return password


def enrollYubikey(digits=6, APPEND_CR=True, debug=False, access_key=None,
                  new_access_key=None, slot=1,
                  mode=MODE_OATH,
                  fixed_string=None,
                  len_fixed_string=None,
                  prefix_serial=False,
                  challenge_response=False):
    """
    :param mode: Defines if the yubikey should be enrolled in OATH mode (1) or
        Yubico Mode (2)
    :type mode: integer
    
    :param fixed_string: A fixed string can be added in front of the output.
        If set to None, a random string will be generated
    :type fixed_string: string

    :param access_key: A hex string, that needs to be passed to programm the
        yubikey
    :param new_access_key: A hex string, that is set as the new access_key
    
    :param len_fixed_string: This specified the length of the random fixed
        string.
    :type len_fixed_string: integer
    
    :return: tuple of key, serial, fixed_string
    """
    print("Initializing Yubikey in mode {0!s}.".format(mode))
    YK = yubico.yubikey.find_key(debug=debug)
    firmware_version = YK.version()
    serial = "%08d" % YK.serial()
    # The fixed string to be returned
    ret_fixed_string = ""

    v1 = re.match('1.', firmware_version)
    v2 = re.match('2.0.', firmware_version)
    
    if v1 or v2:
        raise YubiError("Your Yubikey is too old. You need Firmware 2.1 or "
                        "above. You are running %s"
                        % firmware_version)

    Cfg = YK.init_config()

    # handle access_key and new_access_key
    if access_key:
        access_key = access_key if access_key[1:] == "h:" else "h:"+access_key
        Cfg.unlock_key(access_key)
    if new_access_key:
        # set new accesskey
        new_access_key = new_access_key if new_access_key[1:] == "h:" else \
            "h:" + new_access_key
        Cfg.access_key(new_access_key)

    # default fixed string length is 0, but 6 for MODE_YUBICO
    if len_fixed_string is None:
        if mode == MODE_YUBICO:
            len_fixed_string = 6
        else:
            len_fixed_string = 0

    if mode == MODE_YUBICO:
        key = binascii.hexlify(os.urandom(16))
        uid = os.urandom(yubico.yubikey_defs.UID_SIZE)
        if challenge_response:
            #Cfg.mode_challenge_response('h:' + key, type="OTP")
            raise YubiError("privacyIDEA only supports the OATH challenge "
                            "Response mode at the moment!")
        else:
            Cfg.mode_yubikey_otp(uid, b'h:' + key)

    elif mode == MODE_OATH:
        key = binascii.hexlify(os.urandom(20))
        if challenge_response:
            Cfg.mode_challenge_response(b'h:' + key, type="HMAC")
        else:
            try:
                # set hmac mode with key and 6 digits
                # Try if we got 0.0.5
                Cfg.mode_oath_hotp(b'h:' + key, digits=digits)
            except TypeError:
                # We seem to have 0.0.4
                Cfg.mode_oath_hotp(b'h:' + key, bytes=digits)

    elif mode == MODE_STATIC:
        key = binascii.hexlify(os.urandom(16))
        Cfg.aes_key(b'h:' + key)
        Cfg.config_flag('STATIC_TICKET', True)
        
    else:
        raise YubiError("Unknown OTP mode specified.")

    # Do the fixed string:
    if prefix_serial:
        ret_fixed_string = serial
    elif fixed_string:
        ret_fixed_string = fixed_string
    elif len_fixed_string:
        if mode == MODE_YUBICO:
            ret_fixed_string = binascii.unhexlify('ff') + os.urandom(
                len_fixed_string - 1)
        else:
            ret_fixed_string = os.urandom(len_fixed_string)
    Cfg.fixed_string(ret_fixed_string)
    ret_fixed_string = modhex_encode(ret_fixed_string)

    # set CR behind OTP value
    Cfg.ticket_flag('APPEND_CR', APPEND_CR)
    Cfg.extended_flag('SERIAL_API_VISIBLE', True)
    
    YK.write_config(Cfg, slot=slot)

    return key, serial, ret_fixed_string


def main():
    file_template = """<Tokens>
<Token serial="%s">
    <CaseModel>5</CaseModel>
    <Model>yubikey</Model>
    <ProductionDate>%s</ProductionDate>
    <ProductName>Yubikey 2.2</ProductName>
    <Applications>
        <Application ConnectorID="{a61c4073-2fc8-4170-99d1-9f5b70a2cec6}">
        <Seed>%s</Seed>
        <MovingFactor>1</MovingFactor>
        </Application>
    </Applications>
</Token>
</Tokens>"""

    import datetime
    from getopt import getopt, GetoptError

    OUTFILE = ""
    today = datetime.date.today().strftime("%m/%d/%Y")

    try:
        opts, args = getopt(sys.argv[1:], "o:",
                ['outfile='])

    except GetoptError:
        print("There is an error in your parameter syntax:")
        print("o, outfile=    the name of the output file")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('o', '--outfile'):
            print("setting output file : ", arg)
            OUTFILE = arg

    #
    # example of usage
    #
    try:
        #otpkey, serial = enrollYubikey( debug= False ,
        #                                access_key = binascii.unhexlify('121212121212'),
        #                                unlock_key = binascii.unhexlify('121212121212'))
        otpkey, serial, fixed_string = enrollYubikey(debug=False)
        print("Success: serial: %s, otpkey: %s." % (serial, otpkey))
        #
        # Now we write to a file
        #
        if "" == OUTFILE:
            OUTFILE = "yubikey-%s.xml" % serial
        f = open(OUTFILE, 'w')
        f.write(file_template % ("YUBI%s" % serial, today, otpkey))
        f.close()

    except yubico.yubico_exception.YubicoError as  e:
        print("ERROR: %s" % str(e))
        sys.exit(1)
    except YubiError as e:
        print("Error: %s" % e.value)


class YubikeyPlug(object):

    def __init__(self):
        self.last_serial = None

    def wait_for_new_yubikey(self, timeout=None):
        '''
        This functions waits for a new yubikey to be inserted
        '''
        found = False
        while 1:
            try:
                sleep(1)
                YK = yubico.yubikey.find_key()
                #firmware_version = YK.version()
                serial = "%08d" % YK.serial()

                if serial != self.last_serial:
                    self.last_serial = serial
                    print("\nFound Yubikey with serial %r\n" % serial)
                    found = True
                    break;
            except USBError:
                sys.stdout.write('u')
                sys.stdout.flush()
            except YubiKeyError:
                sys.stdout.write('.')
                sys.stdout.flush()

        return found


if __name__ == "__main__":
    main()

