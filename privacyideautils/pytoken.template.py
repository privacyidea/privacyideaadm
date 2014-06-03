#!/usr/bin/python
# -*- coding: utf-8 -*-

" HMAC-OTP Software Token "

import os, sys, platform
import binascii
import hmac
from hashlib import sha1
import struct

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
    counter_file = ""

    system = platform.system()
    if system == "Linux":
	counter_file = os.path.join(os.getenv("HOME"), ".pytoken-counter")
    elif system == "Windows":
        counter_file = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "\pytoken-counter")
    else:
        print "I do not know your operating system"
        sys.exit(1)


    if os.path.exists(counter_file):
        counter = int(file(counter_file).read().strip()) + 1
    else:
        counter = 0

    hexkey = "<put_your_hmac_here>"

    key = binascii.a2b_hex(hexkey)
    otp = HmacOtp(key, counter=counter).generate()

    print "Your OTP with number %d is %06d." % (counter, otp)
    print "Happy Authenticating!"

    file(counter_file, 'w').write(str(counter))

if __name__ == '__main__':
    main()

