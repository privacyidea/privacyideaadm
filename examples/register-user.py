#!/usr/bin/python
# -*- coding: utf-8 -*-
from privacyideautils.clientutils import (showresult,
                                          PrivacyIDEAClientError,
                                          privacyideaclient)

ADMIN = "super"
PASSWORD = "test"
URL = "http://127.0.0.1:5000"
USER_LIST = ["cornelius", "corny", "root"]
# we assume the default realm
REALM = "defrealm"

client = privacyideaclient(ADMIN, PASSWORD, URL,
                           no_ssl_check=True)


resp = client.userlist({})

users = resp.data.get("result").get("value")
for user in users:
    username = user.get("username")
    print("Fetching username %s" % username)
    try:
        resp = client.listtoken({"user": user,
                                 "realm": REALM})
        print(resp.data.get("result"))
    except PrivacyIDEAClientError:
        print("User not found")


for user in USER_LIST:
    print("Enrolling user %s " % user)
    print(30*"=")
    resp = client.inittoken({"user": user,
                           "type": "registration"})
    showresult(resp.data)



