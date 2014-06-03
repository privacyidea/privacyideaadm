#!/usr/bin/python
# -*- coding: utf-8 -*-

" HMAC-OTP Software Token "

import os, sys, platform
import binascii
import hmac
from hashlib import sha1
import struct
from getopt import getopt, GetoptError


class HmacOtp:
    def __init__(self, key, counter=0, digits=6):
        self.key = key
        self.counter = counter
        self.digits = digits

    def hmac(self, key=None, counter=None):
        key = key or self.key
        counter = counter or self.counter
        digest = hmac.new(key, struct.pack(">Q", counter), sha1)
        return digest.digest()

    def truncate(self, digest):
        offset = ord(digest[-1:]) & 0x0f

        binary = (ord(digest[offset + 0]) & 0x7f) << 24
        binary |= (ord(digest[offset + 1]) & 0xff) << 16
        binary |= (ord(digest[offset + 2]) & 0xff) << 8
        binary |= (ord(digest[offset + 3]) & 0xff)

        return binary % (10 ** self.digits)

    def generate(self, key=None, counter=None):
        key = key or self.key
        counter = counter or self.counter
        otp = self.truncate(self.hmac(key, counter))
        self.counter = counter + 1
        return otp


def main():

    HEXKEY = "400edad7f3e8939c7ffa2d57d1bed94695bfd46c"
    TIMESTEP = 60
    OFFSET = 0

    def usage():
       print "o, offset=      tokenoffset in seconds"

    try:
        opts, args = getopt(sys.argv[1:], "o:",
                ['offset=', '--help'])

    except GetoptError:
        print "There is an error in your parameter syntax:"
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('o', '--offset'):
            print "setting offset : ", arg
            OFFSET = int(arg)




    from time import time
    counter = int((time() + OFFSET) / TIMESTEP + 0.5)

    key = binascii.a2b_hex(HEXKEY)
    otp = HmacOtp(key, counter=counter).generate()

    print "Your OTP with number %d is %06d." % (counter, otp)
    print "Happy Authenticating!"


if __name__ == '__main__':
    main()

