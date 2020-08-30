# -*- coding: utf-8 -*-
#
#  2020-04-13 Cornelius Kölbel <cornelius.koelbel@netknights.it>
#             migrate to click
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
from __future__ import print_function
import click
import datetime
import logging
import qrcode
import sys
from privacyideautils.clientutils import (showresult,
                                          dumpresult,
                                          privacyideaclient,
                                          __version__)
from privacyideautils.etokenng import initetng
from privacyideautils.initdaplug import init_dongle
from privacyideautils.nitrokey import NitroKey
from privacyideautils.yubikey import (enrollYubikey, YubikeyPlug,
                                      create_static_password, MODE_YUBICO,
                                      MODE_OATH, MODE_STATIC)
from email.mime.text import MIMEText
import smtplib


def cifs_push(config, text):
    '''
    Push the the data text to a cifs share

    :param config: dictionary with the fields cifs_server, cifs_share,
                   cifs_dir, cifs_user, cifs_password
    :type config: dict
    :param text: text to be pushed to the windows share
    :type text: string

    '''
    FILENAME = datetime.datetime.now().strftime("/tmp/%y%m%d-%H%M%S"
                                                "_privacyideaadm.out")
    f = open(FILENAME, 'w')
    f.write(text)
    f.close()

    filename = os.path.basename(FILENAME)

    print("Pushing %s to %s//%s/%s" % (filename,
                                       config.get("cifs_server"),
                                       config.get("cifs_share", ""),
                                       config.get("cifs_dir")))

    args = ["smbclient",
            "//%s\\%s" % (config.get("cifs_server"),
                          config.get("cifs_share", "")),
            "-U", "%s%%%s" % (config.get("cifs_user"),
                              config.get("cifs_password")), "-c",
            "put %s %s\\%s" % (FILENAME,
                               config.get("cifs_dir", "."),
                               filename)]

    p = subprocess.Popen(args,
                         cwd=None,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=False)
    (result, error) = p.communicate()
    _rcode = p.returncode
    print(result)
    print(error)

    try:
        os.remove(FILENAME)
    except Exception as e:
        print("couldn't remove push test file: %r" % e)


def sendmail(config, text):
    """
    Send an email with the text

    :param config: dictionary with the fields mail_from, mail_to, mail_host,
                   mail_subject
    :type config: dict
    :param text: text to be sent via mail
    :type text: string
    """
    if not config.get("mail_to"):
        Exception("mail_to required!")

    if not config.get("mail_host"):
        Exception("mail_host required!")

    print("sending mail to %s" % config.get("mail_to"))
    msg = MIMEText(text)
    sender = config.get("mail_from")
    recipient = config.get("mail_to")
    msg['Subject'] = config.get("mail_subject")
    msg['From'] = sender
    msg['To'] = recipient

    mail = smtplib.SMTP(config.get("mail_host"), config.get("mail_port") or 25)
    mail.ehlo()
    if config.get("mail_tls"):
        mail.starttls()
    if config.get("mail_user"):
        mail.login(config.get("mail_user"), config.get("mail_password"))

    mail.sendmail(sender, [recipient], msg.as_string())
    mail.quit()


@click.group()
@click.pass_context
def token(ctx):
    """
    Manage tokens.
    """
    pass


@token.command()
@click.pass_context
@click.option('-u', '--user', help="List tokens of this user.")
@click.option('-s', '--serial', help="List tokens with this serial.")
@click.option('-c', '--csv', help="Export as csv.", is_flag=True)
@click.option('-e', '--export_fields', help="comma separated list of additional "
                              "fields to export into the CSV export.")
@click.option('--cifs_server', help="If exporting as CSV you can save the "
                              "result to this CIFS server.")
@click.option('--cifs_user', help="If exporting as CSV you can save the "
                              "result to a CIFS server with this username.")
@click.option('--cifs_password', help="If exporting as CSV you can save the "
                              "result to a CIFS server with this password.")
@click.option('--mail_host', help="If exporting as CSV you can send the "
                              "result as mail via this mail host.")
@click.option('--mail_to', help="If exporting as CSV you can send the "
                              "result to this email address.")
def list(ctx, user, serial, csv, export_fields, mail_host, mail_to,
         cifs_server, cifs_user, cifs_password):
    """
    List tokens
    """
    client = ctx.obj["pi_client"]
    param = {}
    if user:
        param["user"] = user
    if serial:
        param["serial"] = serial
    if csv:
        param['outform'] = 'csv'
        if export_fields:
            param['user_fields'] = export_fields
        resp = client.listtoken(param)
        r1 = resp.data
        if mail_host and mail_to:
            sendmail(mail_host, mail_to, r1)
        if cifs_server and cifs_user and cifs_password:
            cifs_push(cifs_server, cifs_user, cifs_password, r1)
    else:
        resp = client.listtoken(param)
        if resp.status == 200:
            r1 = resp.data
            result = r1['result']
            dumpresult(result['status'],
                       result['value']['tokens'])


@token.command()
@click.pass_context
@click.option("--user", help="If a user is specified, the "
                             "token is directly assigned to this user.")
@click.option("--serial", help="This is the new serial number "
                             "of the token")
@click.option("--description", help="The description of the "
                             "token. This can be used to identify the token "
                             "more easily.",
                             default="command line enrolled")
@click.option("--pin", help="The OTP PIN of the token.")
@click.option("--otpkey", help="The OTP key, like the HMAC key")
@click.option("--genkey", help="Generate an HOTP key", is_flag=True)
@click.option("--type", help="The token type",
              type=click.Choice(["hotp", "totp", "pw", "spass", "dpw",
                                      "ssh", "sms", "email", "yubico",
                                      "registration"], case_sensitive=False),
              default="hotp")
@click.option("--etng", help="If specified, an etoken NG will "
                             "be initialized", is_flag=True)
def init(ctx, user, serial, description, pin, otpkey, genkey, type, etng):
    """
    Initialize a token. I.e. create a new token in privacyidea.
    """
    client = ctx.obj["pi_client"]
    param = {}
    param["type"] = type
    param["otpkey"] = otpkey
    if genkey:
        param["genkey"] = 1
    if user:
        param["user"] = user
    if serial:
        param["serial"] = serial
    if description:
        param["description"] = description
    if pin:
        param["pin"] = pin

    if etng:
        tokenlabel = user
        tdata = initetng({'label': tokenlabel,
                          'debug': True})
        if not tdata['userpin'] or not tdata['hmac'] or not tdata['serial']:
            print("No token was added to privacyIDEA: ", tdata['error'])
            sys.exit(1)
        param['serial'] = tdata['serial']
        param['otpkey'] = tdata['hmac']
        param['userpin'] = tdata['userpin']
        param['sopin'] = tdata['sopin']
        print(("FIXME: what shall we do with the eToken password and "
              "SO PIN: ", tdata['userpin'], tdata['sopin']))

    resp = client.inittoken(param)
    print("result: {0!s}".format(resp.status))
    showresult(resp.data)
    if resp.status == 200:
        if not param.get("serial"):
            print("serial: {0!s}".format(resp.data.get("detail", {}).get("serial")))
        if param.get("genkey"):
            print("otpkey: {0!s}".format(resp.data.get("detail", {}).get("otpkey", {}).get("value")))
            googleurl = resp.data.get("detail", {}).get("googleurl", {}).get("value")
            qr = qrcode.QRCode()
            qr.add_data(googleurl)
            qr.print_ascii(tty=True)


@token.command()
@click.pass_context
@click.option("--realm",
              help="The realm for which registration tokens should be enrolled.",
              required=True)
@click.option("--dump", help="Do not send notification email to the user, but dump "
                             "the data to stdout.", is_flag=True)
@click.option("--mail_host", help="Mailserver to send notification.", required=True)
@click.option("--mail_from", help="Mail sender address.", required=True)
@click.option("--mail_subject", help="Mail subject.", required=True)
@click.option("--mail_body", help="Mail body. Should contain %%(username)s "
                                  "and %%(registration)s",
              required=True)
@click.option("--mail_port", help="Port of the mailserver", type=int,
              default=25)
@click.option("--mail_tls", help="If mailserver supports STARTTLS.", default=False,
              is_flag=True)
@click.option("--mail_user", help="Username, if required by mailserver.")
@click.option("--mail_password", help="Password, if required by mailserver.")
@click.option("--mail_subject", help="The subject of the email")
def registration(ctx, realm, dump, mail_host, mail_from, mail_subject,
                 mail_body, mail_port, mail_tls, mail_user, mail_password):
    """
    enroll registration tokens for all users in a realm, who do not have a
    token, yet.
    """
    client = ctx.obj["pi_client"]
    response = client.userlist({"realm": realm})
    data = response.data
    result = data.get('result')
    users = result.get('value')
    tokens = []
    for user in users:
        username = user.get("username")
        email = user.get("email")
        # check, if the user has tokens
        count = get_users_token_num(client, username, realm)
        if count == 0:
            # User has no token, create one.
            print("Creating token for user %s" % username)
            response = client.inittoken({"type": "registration",
                                         "user": username,
                                         "realm": realm})
            result = response.data.get("result")
            detail = response.data.get("detail")
            registrationcode = detail.get("registrationcode")
            serial = detail.get("serial")
            tokens.append({"username": username,
                           "email": email,
                           "serial": serial,
                           "registration": registrationcode})

    for token in tokens:
        if dump:
            print(token)
        else:
            print("Sending email to %(email)s" % token)
            config = {"mail_to": token.get("email"),
                      "mail_from": mail_from,
                      "mail_host": mail_host,
                      "mail_port": mail_port,
                      "mail_tls": mail_tls,
                      "mail_user": mail_user,
                      "mail_password": mail_password}
            sendmail(config, mail_body % token)


@token.command()
@click.pass_context
@click.option("--yubiprefix", help="A prefix that is outputted "
                                   "by the yubikey",
              default="")
@click.option("--yubiprefixrandom", help="A random prefix "
                                         "of length. For YUBICO mode the default will be 6!",
              type=int, default=0)
@click.option("--yubiprefixserial",
              help="Use the serial number of "
                   "the yubikey as prefix.", is_flag=True)
@click.option("--yubimode", help="The mode the yubikey should "
                                 "be initialized in. (default=OATH)",
              type=click.Choice([MODE_OATH, MODE_YUBICO, MODE_STATIC]),
              default="OATH")
@click.option("--filename",
              help="If the initialized yubikeys should not be "
                   "sent to a privacyIDEA server the otpkeys can "
                   "be written to a CSV file, to be imported "
                   "later.")
@click.option("--yubislot", help="The slot of the yubikey, that "
                                 "is initialized (default=1)",
              type=click.Choice(["1", "2"]),
              default="1")
@click.option("--yubicr",
              help="Initialize the yubikey in challenge/"
                   "response mode.",
              is_flag=True)
@click.option("--realm",
              help="Enroll the yubikey to the given realm.")
@click.option("--description", help="The description of the "
                                    "token. This can be used to identify the token "
                                    "more easily.",
              default="command line enrolled")
@click.option("--access",
              help="Use this hexlified access key to programm the "
                   "yubikey")
@click.option("--newaccess",
              help="Set a new access key, so that the yubikey will"
                   "only programmable with this new access key. "
                   "You can reset the access key by setting the "
                   "new access key to '000000000000'.")
def yubikey_mass_enroll(ctx, yubiprefix, yubiprefixrandom, yubiprefixserial,
                        yubimode, filename, yubislot, yubicr, description, access, newaccess, realm):
    """
    Initialize a bunch of yubikeys
    """
    client = ctx.obj["pi_client"]
    yp = YubikeyPlug()
    while True:
        print("\nPlease insert the next yubikey.", end=' ')
        sys.stdout.flush()
        submit_param = {}
        _ret = yp.wait_for_new_yubikey()
        otpkey, serial, prefix = enrollYubikey(
            debug=False,
            APPEND_CR=not yubicr,
            prefix_serial=yubiprefixserial,
            fixed_string=yubiprefix,
            len_fixed_string=yubiprefixrandom,
            slot=int(yubislot),
            mode=yubimode,
            challenge_response=yubicr,
            access_key=access,
            new_access_key=newaccess)
        if yubimode == MODE_OATH:
            # According to http://www.openauthentication.org/oath-id/prefixes/
            # The OMP of Yubico is UB
            # As TokenType we use OM (oath mode)
            submit_param = {'type': 'HOTP',
                            'serial': "UBOM%s_%s" % (serial, yubislot),
                            'otpkey': otpkey,
                            'description': description,
                            'otplen': 6,
                            'yubikey.prefix': prefix}
            if yubicr:
                submit_param['type'] = 'TOTP'
                submit_param['timeStep'] = 30

        elif yubimode == MODE_STATIC:
            password = create_static_password(otpkey)
            # print "otpkey   ", otpkey
            # print "password ", password
            submit_param = {'serial': "UBSM%s_%s" % (serial, yubi_slot),
                            'otpkey': password,
                            'type': "pw",
                            'description': description,
                            'yubikey.prefix': prefix}

        elif yubimode == MODE_YUBICO:
            yubi_otplen = 32
            if prefix:
                yubi_otplen = 32 + len(prefix)
            elif yubiprefixrandom:
                # default prefix length for MODE_YUBICO is 6
                if yubiprefixrandom is None:
                    yubiprefixrandom = 6
                yubi_otplen = 32 + (yubiprefixrandom * 2)
            # According to http://www.openauthentication.org/oath-id/prefixes/
            # The OMP of Yubico is UB
            # As TokenType we use AM (AES mode)
            submit_param = {'type': 'yubikey',
                            'serial': "UBAM%s_%s" % (serial, yubislot),
                            'otpkey': otpkey,
                            'otplen': yubi_otplen,
                            'description': description,
                            'yubikey.prefix': prefix}

        if realm:
            submit_param['realm'] = realm

        if filename:
            # Now we write the data to a file
            f = open(filename, mode="a")
            f.write("%(serial)s, %(otpkey)s, %(type)s, %(otplen)s\n" %
                    submit_param)
            f.close()
        else:
            # The token is submitted to the privacyIDEA system
            resp = client.inittoken(submit_param)
            print(resp.status)
            showresult(resp.data)


@token.command()
@click.pass_context
@click.option("--nitromode", help="Either HOTP or TOTP",
              type=click.Choice(["HOTP", "TOTP"]), default="HOTP")
@click.option("--slot", help="The slot of the Nitrokey, that is initialized (default=0)",
              type=click.Choice(["{0!s}".format(x) for x in range(0, 16)]),
              default="0")
@click.option("--description",
              help="The description of the token. This can be used to identify the token "
                   "more easily.")
@click.option("--pin", help="The Admin password of the Nitrokey")
@click.option("--digits", help="The number of allowed OTP digits.",
                         type=click.Choice(["6", "8"]), default=6)
@click.option("--slotname", help="The name of the OTP slot.", default="privacyIDEA")
def nitrokey_mass_enroll(ctx, nitromode, slot, description, pin, digits, slotname):
    """
    Initialize a bunch of Nitrokeys
    """
    client = ctx.obj["pi_client"]
    NK = NitroKey()
    if nitromode == "TOTP":
        raise Exception("At the moment we only support HOTP.")
    slot = int(slot)
    digits = int(digits)
    print("\nWe are going to initialize your Nitrokeys. Please assure, "
          "that no Nitrokey-App is active!\n")
    if not password:
        # Ask for the Nitrokey administrator password
        password = getpass.getpass(prompt="Please enter the Nitrokey "
                                          "Administrator Password:")

    NK.admin_login(password)
    while True:
        print("Please insert the next Nitrokey!")
        input("Press [ENTER] when ready.")

        print("Initializing keys")
        otp_key = NK.init_hotp(slot, slotname, digits=digits)
        status = NK.status()
        serial = "".join(status.get("card_serial", "").split()).upper()
        print("Enrolled token  with serial: {0!s}.".format(serial))

        param = {}
        param["serial"] = "NK{0!s}_{1!s}".format(serial, slot)
        param["otpkey"] = otp_key
        param["otplen"] = int(digits)
        param["type"] = nitromode
        param["description"] = description or slotname
        resp = client.inittoken(param)
        showresult(resp.data)

    NK.logout()


@token.command()
@click.pass_context
@click.option("-k", "--keyboard", is_flag=True,
              help="If this option is set, the daplug will simulate "
                   "a keyboard and type the OTP value when plugged in.")
@click.option("--hidmap", help="Specify the HID mapping. The default HID "
                               "mapping is 05060708090a0b0c0d0e. Only use this, "
                               "if you know "
                               "what you are doing!",
              default="05060708090a0b0c0d0e")
@click.option("--otplen", type=click.Choice(["6", "8"]),
              help="Specify if the OTP length should be 6 or 8.")
def daplug_mass_enroll(ctx, keyboard, hidmap, otplen):
    """
    Initialize a bunch of daplug dongles.
    """
    client = ctx.obj["pi_client"]
    (serial, hotpkey) = init_dongle(keyboard=keyboard,
                                    mapping=hidmap,
                                    otplen=otplen)
    if serial:
        param = {}
        param["serial"] = "DPLG%s" % serial
        param["otpkey"] = hotpkey
        param["otplen"] = int(otplen)
        param["type"] = "daplug"
        param["description"] = "daplug dongle"
        r1 = client.inittoken(param)
        showresult(r1)


@token.command()
@click.pass_context
@click.option("--label", help="The label of the eToken NG OTP.",
              default="privacyIDEAToken")
@click.option("--description", help="Description of the token.",
              default="mass enrolled")
def etokenng_mass_enroll(ctx, label, description):
    """
    Enroll a bunch of eToken NG OTP.
    """
    print("""Mass-Enrolling eToken NG OTP.
    !!! Beware the tokencontents of all tokens will be deleted. !!!

    Random User PINs and SO-PINs will be set.
    The SO-PIN will be stored in the Token-Database.
    """)
    client = ctx.obj["pi_client"]
    param = {}
    while True:
        answer = input("Please insert the next eToken NG"
                       " and press enter (x=Exit): ")
        if "x" == answer.lower():
            break
        tdata = initetng({'label': label,
                          'debug': False,
                          'description': description})
        if not tdata['userpin'] or not tdata['hmac'] or not tdata['serial']:
            print("No token was added to privacyIDEA:", tdata['error'])
            sys.exit(1)
        param['serial'] = tdata['serial']
        param['otpkey'] = tdata['hmac']
        param['userpin'] = tdata['userpin']
        param['sopin'] = tdata['sopin']
        r1 = client.inittoken(param)
        showresult(r1)


@token.command()
@click.pass_context
@click.option("--serial", help="Serial number of the token to assign", required=True)
@click.option("--user", help="The user, who should get the token", required=True)
def assigntoken(ctx, serial, user):
    """
    Assign a token to a user
    """
    client = ctx.obj["pi_client"]
    param = {}
    param["user"] = user
    param["serial"] = serial
    response = client.assigntoken(param)
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="Serial number of the token to unassign", required=True)
def unassigntoken(ctx, serial):
    """
    Remove a token from a user
    """
    client = ctx.obj["pi_client"]
    response = client.unassigntoken({"serial": serial})
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("-f", "--file", help="The token file to import", required=True)
def importtoken(args, client):
    """
    Import a token file
    """
    client = ctx.obj["pi_client"]
    response = client.importtoken({'file': file})
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="serial number of the token to disable")
@click.option("--user", help="The username of the user, whose tokens should be disabled")
def disable(ctx, serial, user):
    """
    Disable token by serial or user name
    """
    client = ctx.obj["pi_client"]
    param = {}
    if serial:
        param["serial"] = serial
    if user:
        param["user"] = user
    response = client.disabletoken(param)
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="serial number of the token to enable")
@click.option("--user", help="The username of the user, whose tokens should be enabled")
def enabletoken(ctx, serial, user):
    """
    Enable token by serial or user name
    """
    client = ctx.obj["pi_client"]
    param = {}
    if serial:
        param["serial"] = serial
    if user:
        param["user"] = user
    response = client.enabletoken(param)
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="serial number of the token to remove")
@click.option("--user", help="The username of the user, whose tokens should be deleted")
@click.option("--realm", help="Delete all tokens of the given type in this realm.")
@click.option("--type", help="Delete all tokens of this type in the given realm.")
def delete(ctx, serial, user, realm, type):
    """
    Delete tokens based on serial, user, realm or token type.
    """
    client = ctx.obj["pi_client"]
    serials = []
    if serial:
        serials = [serial]

    elif user:
        response = client.listtoken({"user": user, "realm": realm})
        value = response.data.get("result", {}).get("value")
        for token in value.get("tokens"):
            serials.append(token.get("serial"))

    elif type:
        if not realm:
            print("If you want to delete a tokentype, you need to specify a realm!")
            sys.exit(1)
        response = client.listtoken({"tokenrealm": realm, "type": type})
        value = response.data.get("result", {}).get("value")
        for token in value.get("tokens"):
            serials.append(token.get("serial"))

    for serial in serials:
        print("Delete token %s" % serial)
        response = client.deletetoken(serial)
        showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="Serial number of the token", required=True)
@click.option("--otp1", help="First OTP value", required=True)
@click.option("--otp2", help="Second consecutive OTP value", required=True)
def resync(ctx, serial, otp1, otp2):
    """
    Resynchronize the token
    """
    client = ctx.obj["pi_client"]
    param = {}
    param["serial"] = serial
    param["otp1"] = otp1
    param["otp2"] = otp2
    response = client.removetoken(param)
    showresult(response.data)


@token.command()
@click.pass_context
@click.option("--serial", help="Serial number of the token")
@click.option("--user", help="User, whose token should be modified")
@click.option("--pin", help="Set the OTP PIN of the token")
@click.option("--otplen", help="Set the OTP lenght of the token. Usually this is 6 or 8.",
              type=click.Choice(["6", "8"]))
@click.option("--syncwindow", help="Set the synchronizatio window of a token.", type=int)
@click.option("--maxfailcount", help="Set the maximum fail counter of a token.", type=int)
@click.option("--counterwindow", help="Set the window of the counter.", type=int)
@click.option("--hashlib", help="Set the hashlib.",
              type=click.Choice(["sha1", "sha2", "sha256", "sha384", "sha512"]))
@click.option("--timewindow", help="Set the timewindow.", type=int)
@click.option("--timestep", help="Set the timestep. Usually 30 or 60.", type=int)
@click.option("--timeshift", help="Set the clock drift, the time shift.", type=int)
@click.option("--countauthsuccessmax", help="Set the maximum allowed successful authentications",
              type=int)
@click.option("--countauthsuccess", help="Set the number of successful authentications",
              type=int)
@click.option("--countauth", help="Set the number of authentications", type=int)
@click.option("--countauthmax", help="Set the maximum allowed of authentications", type=int)
@click.option("--validityperiodstart", help="Set the start date when the token is usable.")
@click.option("--validityperiodend", help="Set the end date till when the token is usable.")
@click.option("--description", help="Set the description of the token.")
@click.option("--phone", help="Set the phone number of the token.")
def set(ctx, serial, user, pin, otplen, syncwindow, maxfailcount, counterwindow,
        hashlib, timewindow, timestep, timeshift, countauthsuccessmax, countauthsuccess,
        countauth, countauthmax, validityperiodstart, validityperiodend, description, phone):
    """
    Set certain attributes of a token
    """
    client = ctx.obj["pi_client"]
    param = {}
    if serial:
        param["serial"] = serial
    if user:
        param["user"] = user
    if pin:
        param["pin"] = pin
    if otplen:
        param["OtpLen"] = otplen
    if syncwindow:
        param["SyncWindow"] = syncwindow
    if maxfailcount:
        param["MaxFailCount"] = maxfailcount
    if counterwindow:
        param["CounterWindow"] = counterwindow
    if hashlib:
        param["hashlib"] = hashlib
    if timewindow:
        param["timeWindow"] = timewindow
    if timestep:
        param["timeStep"] = timestep
    if timeshift:
        param["timeShift"] = timeshift
    if countauthsuccessmax:
        param["countAuthSuccessMax"] = countauthsuccessmax
    if countauthsuccess:
        param["countAuthSuccess"] = countauthsuccess
    if countauthmax:
        param["countAuthMax"] = countauthmax
    if countauth:
        param["countAuth"] = countauth
    if validityperiodstart:
        param["validityPeriodStart"] = validityperiodstart
    if validityperiodend:
        param["validityPeriodEnd"] = validityperiodend
    if description:
        param["description"] = description
    if phone:
        param["phone"] = phone

    response = client.set(param)
    showresult(response.data)
