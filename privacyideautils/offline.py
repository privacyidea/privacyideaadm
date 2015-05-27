#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  privacyIDEA
#  2015-03-16 Cornelius Kölbel, <cornelius@privacyidea.org>
#             initial writeup to fetch offline auth_items
#
#  (c) 2015 Cornelius Kölbel, cornelius@privacyidea.org
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
"""
Used to do offline authentication
"""
import base64
from os import urandom
import binascii
from hashlib import sha256
import sqlite3


def salted_hash_256(data, salt_length=16, salt=None):
    if not salt:
        b_ret = urandom(salt_length)
        salt = binascii.hexlify(b_ret)
    h = '{SSHA256}' + base64.b64encode(sha256(data + salt).digest() + salt)
    return h


def verify_salted_hash_256(data, h, salt_length=16):
    h_raw = h[len('{SSHA256}'):]
    h_bin = base64.b64decode(h_raw)
    salt = h_bin[-salt_length:]
    h_test = salted_hash_256(data, salt=salt)
    return h == h_test


def check_otp(user, otp, sqlfile="offlineotp.sqlite", window=10):
    """
    compare the given otp values with the next hashes of the user.

    DB entries older than the matching counter will be deleted from the
    database.

    :param user: The local user in the sql file
    :param otp: The otp value
    :param sqlfile: The sqlite file
    :return: True or False
    """
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    c.execute("SELECT * FROM authitems WHERE user='%s' ORDER by counter" % user)
    for x in range(0, window):
        r = c.fetchone()

        print r


def save_auth_item(sqlfile, authitem):
    """
    Save the given authitem to the sqlite file to be used later for offline
    authentication.

    There is only one table in it with the columns:

        username, counter, otp

    :param sqlfile: An SQLite file. If it does not exist, it will be generated.
    :type sqlfile: basestring
    :param authitem: A dictionary with all authitem information being:
    username, count, and a response dict with counter and otphash.

    :return:
    """
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    # Create the table if necessary
    try:
        c.execute("CREATE TABLE authitems "
                  "(counter int, user text, tokenowner text, otp text)")
    except:
        pass
    user = authitem.get("user")
    tokenowner = authitem.get("username")

    for counter, otphash in authitem.get("response").iteritems():
        # Insert the OTP hash
        c.execute("INSERT INTO authitems (counter, user, tokenowner, otp) "
                  "VALUES ('%s','%s','%s','%s')"
                  % (counter, user, tokenowner, otphash))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
