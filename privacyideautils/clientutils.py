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
This module is used for the communication of
the python based management clients
privacyidea-adm
'''

import urllib2
import httplib
import urllib
import re
import random
import sys
import logging.handlers
import cookielib
import traceback
import pprint

if sys.version_info[0:2] >= (2, 6):
    import json
else:
    import simplejson as json
import gettext

_ = gettext.gettext

TIMEOUT = 5
etng = False


file_opts = ['rf_file=']
ldap_opts = ['rl_uri=', 'rl_basedn=', 'rl_binddn=',
             'rl_bindpw=', 'rl_timeout=', 'rl_loginattr=',
             'rl_searchfilter=', 'rl_userfilter=',
             'rl_attrmap=']
ldap_opts_map = {'rl_uri': 'LDAPURI',
                 'rl_basedn': 'LDAPBASE',
                 'rl_binddn': 'BINDDN',
                 'rl_bindpw': 'BINDPW',
                 'rl_timeout': 'TIMEOUT',
                 'rl_searchfilter': 'LDAPSEARCHFILTER',
                 'rl_userfilter': 'LDAPFILTER',
                 'rl_attrmap': 'USERINFO',
                 'rl_loginattr': 'LOGINNAMEATTRIBUTE'
                 }


def showresult(rv):
    try:
        pp = pprint.PrettyPrinter(indent=4)
        print pp.pformat(rv['result'])
    except:
        print rv


def initetng():
    pass


class privacyIDEAClientError(Exception):
    '''
    This class is used to throw client exceptions.
    '''
    def __init__(self, eid=10, description="privacyIDEAClientError"):
        self.id = eid
        self.description = description
        
    def getId(self):
        return self.id
    
    def getDescription(self):
        return self.description
    
    def __str__(self):
        # here we lookup the error id - to translate
        return repr("ERR" + str(self.id) + ": " + self.description)


class pyToken:
    '''
    This class is used to generate a pyToken,
    which is a python based soft-token.
    '''
    def __init__(self, keylen=256, template="pytoken.template.py"):
        self.keylen = keylen
        self.template = template
        self.serial = hex(random.getrandbits(8 * 4))
        self.serial = "pT" + self.serial[2:-1]
        self.hmackey = hex(random.getrandbits(self.keylen))
        self.hmackey = self.hmackey[2:-1]

    def getSerial(self):
        return self.serial

    def getHMAC(self):
        return self.hmackey

    def createToken(self, user):
        # read replace and dump
        f = open(self.template)
        tfile = f.readlines()
        f.close
        usertoken = ""
        for line in tfile:
            p = re.compile('<put_your_hmac_here>')
            mt = p.search(line)
            if mt:
                line = p.sub(self.hmackey, line)
            usertoken = usertoken + line
        return usertoken


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    '''
    This Class is used to do the client cert auth with urllib2
    found at:
    http://www.osmonov.com/2009/04/client-certificates-with-urllib2.html
    '''
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        '''
        Rather than pass in a reference to a connection class, we pass in
        a reference to a function which, for all intents and purposes,
        will behave as a constructor
        '''
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host,
                                       key_file=self.key,
                                       cert_file=self.cert)


class privacyideaclient:
    '''
    This class is created to hold a connection to the privacyIDEA server
    '''
    def __init__(self, protocol, url, admin=None, adminpw=None,
                 cert=None, key=None, proxy=None,
                 authtype="Digest", adminrealm=""):
        '''
        arguments:
            The class is created with the parameters
                protocol:   either http or https
                url:        the url of the privacyIDEA server. It consists of
                            the hostname and the port like:
                            localhost:443
            Optional parameters:
                admin/adminpw: If the privacyIDEA server is configured to
                               use digest auth,
                               these are the credentials to authenticate to the
                               privacyIDEA server
                cert/key:      If the privacyIDEA server is configured to use
                               client certificate authentication, these are the
                               filenames of the files holding the certificate
                               and the key.
                 
        description:
            At the moment you can either authenticate via digest auth or
            via client certificates. It is not possible to combine the two
            authentication methods.
        '''
        self.protocol = protocol
        self.url = url
        self.admin = admin
        self.adminpw = adminpw
        self.adminrealm = adminrealm
        self.cert = cert
        self.key = key
        self.proxy = proxy
        self.logging = False
        self.authtype = authtype
        self.log = logging.getLogger('privacyideaclient')
        self.cookie_jar = cookielib.CookieJar()
        self.session = ""
        if (self.admin and self.adminpw):
            self.login()

    def setLogging(self, logtoggle=False, param={}):
        self.logging = logtoggle
        self.LOG_FILENAME = param['LOG_FILENAME']
        self.LOG_COUNT = param['LOG_COUNT']
        self.LOG_SIZE = param['LOG_SIZE']
        self.LOG_LEVEL = param['LOG_LEVEL']
        if self.logging:
            self.log.setLevel(self.LOG_LEVEL)
            if hasattr(self, "handler"):
                self.log.removeHandler(self.handler)
            self.handler = logging.handlers.RotatingFileHandler(
                self.LOG_FILENAME,
                maxBytes=self.LOG_SIZE,
                backupCount=self.LOG_COUNT)
            self.formatter = logging.Formatter("[%(asctime)s][%(name)s]"
                                               "[%(levelname)s]:%(message)s")
            self.handler.setFormatter(self.formatter)
            self.log.addHandler(self.handler)
            self.log.debug("Logging initialized")
        else:
            self.log.debug("Logging disabled")
            if hasattr(self, "handler"):
                self.log.removeHandler(self.handler)

    def setcredentials(self, protocol, url, admin=None, adminpw=None,
                       cert=None, key=None, proxy=None,
                       authtype="Digest", adminrealm=""):
        '''
        arguments:
            The same arguments as when initializing the instance.
            
        description:
            This method can be used, when i.e. the authentication credentials
            need to be changed. If the admin tried to authenticate with
            username /password and he mistyped the password, this function can
            be used, to reset the credentials.
        '''
        self.protocol = protocol
        self.url = url
        self.admin = admin
        self.adminpw = adminpw
        self.adminrealm = adminrealm
        self.cert = cert
        self.key = key
        self.proxy = proxy
        self.authtype = authtype
        try:
            self.login()
        except:
            pass
        if self.logging:
            self.log.info("[setcredentials]: Credentials set successfully.")

    def connect(self, path, param, data={}, json_format=True):
        '''
        arguments:
            path:
                The path argument takes the controller path/method. This can be
                /admin/show
                /admin/init
                /admin/...
                /validate/check
                /validate/simplecheck
                /system/...
                
            param:
                The param is a dictionary of the parameters, that need to be
                passed to the privacyIDEA server controller for the specified
                method.

            data:
                The data, that would be passed in a POST request.
                As soon as the parameter data is provided,
                we'll do a POST request.
                
            json_format:
                The response of the API request is a json format
                
        returns:
            Returns the JSON result as a dictionary.
                
        exceptions:
            In case of connection errors it raises a
            privacyIDEAClientError exception.
        '''
        p = urllib.urlencode(param)
        d = ""
        if len(data) > 0:
            # We got data, so we will do a POST request.
            d = urllib.urlencode(data)
        else:
            # We do a normal GET request
            d = ""
        if self.logging:
            self.log.debug("[connect]: data=" + d)
            self.log.debug("[connect]: type of data: %s" % type(d))
            self.log.info("[connect]: path=" + path)
            self.log.debug("[connect]: param=" + p)

        try:
            # Proxy handler:
            proxy_handler = urllib2.ProxyHandler({})
            # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
            if self.proxy:
                proxy_handler = urllib2.ProxyHandler({self.protocol: self.protocol + '://' + self.proxy + '/'})
                # TODO: Proxy Authentication
                # proxy_auth_handler.add_password(None, self.protocol+'://'+self.url, self.proxyuser, self.proxypass)

            cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
            opener = urllib2.build_opener(proxy_handler, cookie_handler)
            # ...and install it globally so it can be used with urlopen.
            urllib2.install_opener(opener)

            f = urllib2.urlopen(urllib2.Request(self.protocol + '://' + self.url + path + '?session=' + self.session + '&' + p, d))

        except Exception as e:
            if self.logging:
                self.log.error("[connect]: Error connecting to privacyIDEA service: %s" % str(e))
                self.log.error("[connect]: %s" % traceback.format_exc())
            print "[connect]: %s" % traceback.format_exc()
            raise privacyIDEAClientError(1006, _("Error connecting to privacyIDEA service: %s" % str(e)))

        # Now evaluate the response.
        if not json_format:
            rv = f.read()
        else:
            status = False
            try:
                rv = json.load(f)
                if rv.get("result"):
                    # in case of normal json output
                    status = rv['result']['status']
                elif rv.get("rows"):
                    # in case of flexigrid output
                    # like with /audit/search
                    status = True
            except:
                if self.logging:
                    self.log.error("[connect]: Internal JSON error. Could not interpret the privacyIDEA server response: %s" % f)
                raise privacyIDEAClientError(1003, _("Internal JSON error. Could not interpret the privacyIDEA server response:  %s") % f)
    
            if status is False:
                if self.logging:
                    self.log.error("[connect]: Your request to the privacyIDEA server was invalid: " + rv['result']['error']['message'])
                raise privacyIDEAClientError(rv['result']['error']['code'], _("Your request to the privacyIDEA server was invalid: ") + rv['result']['error']['message'])

        return rv

    def login(self):
        # we are doing a post request
        d = urllib.urlencode({"login": self.admin,
                              "realm": self.adminrealm,
                              "password": self.adminpw})
        path = "/account/dologin"

        try:
            # Proxy handler:
            proxy_handler = urllib2.ProxyHandler({})
            # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
            if self.proxy:
                proxy_handler = urllib2.ProxyHandler({self.protocol: self.protocol + '://' + self.proxy + '/'})
                # TODO: Proxy Authentication
                # proxy_auth_handler.add_password(None, self.protocol+'://'+self.url, self.proxyuser, self.proxypass)

            cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
            opener = urllib2.build_opener(proxy_handler, cookie_handler)
            # ...and install it globally so it can be used with urlopen.
            urllib2.install_opener(opener)
            f = urllib2.urlopen(urllib2.Request(self.protocol + '://' + self.url + path, d))

        except Exception as e:
            if self.logging:
                self.log.error("[connect]: Error connecting to privacyIDEA service: %s" % str(e))
                self.log.error("[connect]: %s" % traceback.format_exc())
            print "[connect]: %s" % traceback.format_exc()
            raise privacyIDEAClientError(1006, _("Error connecting to privacyIDEA service: %s" % str(e)))

        rv = f.read()
        
        for cookie in self.cookie_jar:
            if cookie.name == "privacyidea_session":
                self.session = cookie.value.strip('"')
        
        return rv
        
    def userlist(self, param):
        return self.connect('/admin/userlist', param)

    def auditsearch(self, param):
        return self.connect('/audit/search', param)

    def inittoken(self, param):
        return self.connect('/admin/init', param)

    def listtoken(self, param):
        return self.connect('/admin/show', param)

    def getserialbyotp(self, param):
        return self.connect('/admin/getSerialByOtp', param)

    def copytokenpin(self, param):
        return self.connect('/admin/copyTokenPin', param)

    def assigntoken(self, param):
        return self.connect('/admin/assign', param)

    def unassigntoken(self, param):
        return self.connect('/admin/unassign', param)

    def resetfailcounter(self, param):
        return self.connect('/admin/reset', param)

    def resynctoken(self, param):
        return self.connect('/admin/resync', param)

    def tokenrealm(self, serial, realms):
        return self.connect('/admin/tokenrealm',
                            {'serial': serial,
                             'realms': realms})

    def set(self, param):
        '''
        This function is used for many purposes like
            setmaxfail
            setsyncwindow
            setotplen
        This depends on the contents of the param dictionary.
        '''
        return self.connect('/admin/set', param)

    def get_policy(self, param={}):
        return self.connect('/system/getPolicy', param)

    def setscpin(self, param):
        return self.connect('/admin/setPin', param)

    def disabletoken(self, param):
        param['enable'] = 'False'
        return self.connect('/admin/disable', param)

    def enabletoken(self, param):
        param['enable'] = 'True'
        return self.connect('/admin/enable', param)

    def removetoken(self, param):
        return self.connect('/admin/remove', param)

    def readserverconfig(self, param):
        return self.connect('/system/getConfig', param)

    def writeserverconfig(self, param):
        return self.connect('/system/setConfig', param)

    def getrealms(self, param):
        return self.connect('/system/getRealms', param)

    def securitymodule(self, param={}):
        return self.connect('/system/setupSecurityModule', param)

    def setrealm(self, param):
        return self.connect('/system/setRealm', param)

    def deleterealm(self, param):
        return self.connect('/system/delRealm', param)

    def setdefaultrealm(self, param):
        return self.connect('/system/setDefaultRealm', param)

    def deleteconfig(self, param):
        return self.connect('/system/delConfig', param)

    def setresolver(self, param):
        if 'resolver' not in param:
            raise privacyIDEAClientError(1201, _("When setting a resolver, you need to specify 'resolver'."))

        if param['rtype'] == 'FILE':
            if 'rf_file' not in param:
                raise privacyIDEAClientError(1201, _("When setting a flat file resolver, you need to specify 'rf_file'."))
            r1 = self.writeserverconfig({ 'passwdresolver.fileName.' + param['resolver'] : param['rf_file'] })
            return r1

        elif param['rtype'] == 'LDAP':
            for k, v in ldap_opts_map.items():
                if k not in param:
                    raise privacyIDEAClientError(1201, _("When setting an ldap resolver, you need to specify '%s'.") % k)
                r1 = self.writeserverconfig({ 'ldapresolver.' + v + '.' + param['resolver']: param[ k ] })
            return r1
        elif param['rtype'] == 'SQL':
            print "TODO: Doing the Voodoo to set all these config keys"

        return {}

    def deleteresolver(self, param):
        r1 = self.readserverconfig({})
        for (k, _v) in r1['result']['value'].items():
            resolver = k.split(".")
            if len(resolver) == 3:
                if resolver[0] in ("passwdresolver",
                                   "ldapresolver",
                                   "sqlresolver"):
                    if resolver[2] == param['resolver']:
                        print "deleting config key %s." % k
                        self.deleteconfig({'key': k})

    def getresolvers(self, param):
        r1 = self.readserverconfig(param)
        # now we need to split all the resolving stuff.
        newResolver = {}
        for (k, v) in r1['result']['value'].items():
            resolver = k.split(".")
            if len(resolver) == 3:
                if resolver[0]in ("passwdresolver",
                                  "ldapresolver",
                                  "sqlresolver"):
                    if resolver[2] not in newResolver:
                        newResolver[resolver[2]] = {}
                    newResolver[resolver[2]]['type'] = resolver[0]
                    newResolver[resolver[2]][resolver[1]] = v
        r2 = {'result': {'value': newResolver}}
        return r2

    def importtoken(self, param):
        if not param['file']:
            print "Please specify a filename to import the token from"
            return False
        f = open(param['file'])
        tokenfile = f.readlines()
        f.close
        tokenserial = ""
        tokenseed = ""
        tokens = 0
        token_count = 0
        for line in tokenfile:
            mt = re.search('<Token serial=\"(.*)\">', line)
            if mt:
                token_count = token_count + 1
        for line in tokenfile:
            # Format like
            # <Token serial="F800574">
            # <Seed>F71E5AC721B7353735F52494E61B1A62538A0238</Seed>
            mt = re.search('<Token serial=\"(.*)\">', line)
            if mt:
                if tokenseed:
                    print("Error: Got a seed (%r)"
                          "without a serial!" % tokenseed)
                else:
                    tokenserial = mt.group(1)
                    tokens = tokens + 1
                    print("Importing token %r/%r, serial %r" % (tokens,
                                                                token_count,
                                                                tokenserial
                                                                ))
            else:
                ms = re.search('<Seed>(.*)</Seed>', line)
                if ms:
                    tokenseed = ms.group(1)
                    if tokenserial:
                        ret = self.inittoken({ 'serial':tokenserial, 'otpkey':tokenseed, 'description':"Safeword", 'user':'', 'pin':''})
                        if ret['result']['status'] is False:
                            print ret['result']['error']['message']
                        tokenseed = ""
                        tokenserial = ""
                    else:
                        print("Error: Got a seed (%r) without a serial!" % tokenseed)
        print "%i tokens imported." % tokens
        return True


def dumpresult(status, data, tabformat):
    '''
    This function is used to print the Tokenlist in a nice viewable
    ascii table.
    '''
    tabsize = tabformat['tabsize']
    tabstr = tabformat['tabstr']
    tabdelim = tabformat['tabdelim']
    tabvisible = tabformat['tabvisible']
    tabhead = tabformat['tabhead']
    tabentry = tabformat['tabentry']

    # if not result['status']:
    if not status:
        print "The return status is false"
    else:

        head = tabentry

        # Set the default, if no tabformat or a wrong tabformat is passed
        if not len(tabvisible):
            for i in range(0, len(head)):
                tabvisible.append(i)
        if len(tabhead) < len(head):
            print "tabhead " + str(len(tabhead)) + " head " + str(len(head))
            for i in range(0, len(head)):
                tabhead.append('head')
        if len(tabsize) < len(head):
            for i in range(0, len(head)):
                tabsize.append(10)
        if len(tabstr) < len(head):
            for i in range(0, len(head)):
                tabstr.append("%10s")

        # value = result['value']
        # data = value['data']

        i = 0
        for t in tabhead:
            print tabstr[i] % str(t)[:tabsize[i]], tabdelim,
            i = i + 1
        print

        for token in data:
            i = 0
            for t in tabentry:
                # print tabstr[i] % str(token.get(t)).endcode('utf-8') [:tabsize[i]], tabdelim,
                # text=str(token.get(t)).encode('utf-8')
                text = token.get(t)
                if not type(token.get(t)) == unicode:
                    text = str(token.get(t))
                # If we got a IdResClass like useridresolver.PasswdIdResolver.IdResolver.pw2
                # we only want to get the last field
                if t == "privacyidea.IdResClass":
                    r = text.split('.')
                    if len(r) == 4:
                        text = r[3]
                print tabstr[i] % text[:tabsize[i]], tabdelim,
                i = i + 1
            print
