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


@click.group()
@click.pass_context
def realm(ctx):
    """
    Manage realms.
    """
    pass


@realm.command()
@click.pass_context
def list(ctx):
    """
    List all realms
    """
    client = ctx.obj["pi_client"]
    response = client.getrealms()
    showresult(response.data)


@realm.command()
@click.option("--realm", help="The name of the new realm.", required=True)
@click.option("-r", "--resolver", required=True, multiple=True,
              help="The name of the resolver. You can specify several resolvers by "
                   "using several --resolver arguments.")
@click.pass_context
def set(ctx, realm, resolver):
    """
    Create a new realm
    """
    client = ctx.obj["pi_client"]
    param = {}
    param['resolvers'] = ",".join(resolver)
    response = client.setrealm(realm, param)
    showresult(response.data)


@realm.command()
@click.option("--realm", required=True, help="Delete a realm")
@click.pass_context
def delete(ctx, realm):
    """
    Delete the specified realm
    """
    client = ctx.obj["pi_client"]
    response = client.deleterealm(realm)
    showresult(response.data)


@realm.command()
@click.option("--realm", required=True, help="Set default realm")
@click.pass_context
def default(ctx, realm):
    """
    Set the specified realm as default realm
    """
    client = ctx.obj["pi_client"]
    response = client.setdefaultrealm(realm)
    showresult(response.data)
