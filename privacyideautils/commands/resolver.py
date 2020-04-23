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
def resolver(ctx):
    """
    Manage resolvers.
    """
    pass


@resolver.command()
@click.pass_context
def list(ctx):
    """
    List all available resolvers
    """
    client = ctx.obj["pi_client"]
    response = client.getresolver({})
    showresult(response.data)


@resolver.command()
@click.pass_context
@click.option("--resolver", required=True, help="The name of the resolver to delete.")
def deleter(ctx, resolver):
    """
    Delete a resolver
    """
    client = ctx.obj["pi_client"]
    response = client.deleteresolver(resolver)
    showresult(response.data)


@resolver.command()
@click.pass_context
@click.option("--resolver", required=True, help="The name of the new resolver.")
@click.option("--type", required=True,
              type=click.Choice(["LDAP", "SQL", "PASSWD", "SCIM"]),
              help="The type of the new resolver")
@click.option("--filename", help="The filename for Passwdresolvers")
def set(ctx, resolver, type, filename):
    """
    Create a new resolver
    """
    client = ctx.obj["pi_client"]
    if args.type.lower() == "passwd":
        response = client.setresolver(resolver, {"type": type, "filename": filename})
    else:
        print("Resolver Type currently not supported.")
    showresult(response.data)
