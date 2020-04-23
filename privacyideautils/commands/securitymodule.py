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
import getpass
from privacyideautils.clientutils import (showresult,
                                          dumpresult,
                                          privacyideaclient,
                                          __version__)


@click.group()
@click.pass_context
def securitymodule(ctx):
    """
    Manage the security module.
    """
    pass


@securitymodule.command()
@click.pass_context
def init(ctx):
    """
    Initialize the module by entering the password
    """
    client = ctx.obj["pi_client"]
    password = getpass.getpass(prompt="Please enter password for"
                                      " security module:")
    print("Setting the password of your security module")
    response = client.set_hsm(param={"password": str(password)})
    showresult(response.data)


@securitymodule.command()
@click.pass_context
def status(ctx):
    """
    Get the status of the security module
    """
    client = ctx.obj["pi_client"]
    print("This is the configuration of your active Security module:")
    response = client.get_hsm()
    showresult(response.data)
