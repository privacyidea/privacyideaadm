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
import click
import datetime
import logging
from privacyideautils.clientutils import (showresult,
                                          dumpresult,
                                          privacyideaclient,
                                          __version__)
from privacyideautils.clientutils import PrivacyIDEAClientError


@click.group()
@click.pass_context
def certificate(ctx):
    """
    Manage certificates
    """
    pass


@certificate.command()
@click.pass_context
@click.option("--ca", help="Specify the CA where you want to send the CSR to.")
@click.option("--user", help="The user to whom the certificate should be assigned.")
@click.option("--realm", help="The realm of the user to whom the certificate should be assigned.")
@click.argument("requestfile", type=click.File("rb"))
def sign(ctx, requestfile, ca, user, realm):
    """
    Send a certificate signing request to privacyIDEA and have the CSR signed.
    """
    client = ctx.obj["pi_client"]
    param = {"type": "certificate",
             "genkey": 1}
    if requestfile:
        param["request"] = requestfile.read()
    if ca:
        param["ca"] = ca
    if user:
        param["user"] = user
    if realm:
        param["realm"] = realm

    try:
        resp = client.inittoken(param)
        print("result: {0!s}".format(resp.status))
        showresult(resp.data)
        if resp.status == 200:
            if not param.get("serial"):
                print("serial: {0!s}".format(resp.data.get("detail", {}).get("serial")))
    except PrivacyIDEAClientError as e:
        print(e)


@certificate.command()
@click.pass_context
@click.option("--ca", help="Specify the CA where you want to send the CSR to.")
@click.option("--user", help="The user to whom the certificate should be assigned.")
@click.option("--realm", help="The realm of the user to whom the certificate should be assigned.")
@click.option("--pin", help="Set the PIN of the PKCS12 file.")
@click.option("--template", help="Use the specified template.")
def create(ctx, ca, user, realm, pin, template):
    """
    Create a key pair and certificate on the server side.
    """
    client = ctx.obj["pi_client"]
    param = {"type": "certificate",
             "genkey": 1}
    if template:
        param["request"] = requestfile.read()
    if ca:
        param["ca"] = ca
    if user:
        param["user"] = user
    if realm:
        param["realm"] = realm
    if pin:
        param["pin"] = pin

    try:
        resp = client.inittoken(param)
        print("result: {0!s}".format(resp.status))
        showresult(resp.data)
        if resp.status == 200:
            if not param.get("serial"):
                print("serial: {0!s}".format(resp.data.get("detail", {}).get("serial")))
    except PrivacyIDEAClientError as e:
        print(e)
