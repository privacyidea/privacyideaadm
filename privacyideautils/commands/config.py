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
def config(ctx):
    """
    Manage the configuration.
    """
    pass


@config.command()
@click.pass_context
def list(ctx):
    """
    List the configuration of the privacyIDEA server.
    """
    client = ctx.obj["pi_client"]
    response = client.getconfig({})
    showresult(response.data)


@config.command()
@click.pass_context
@click.option('--config', required=True, multiple=True,
              help="Set a configuration value. Use it like --config key=value.")
def set(ctx, config):
    """
    Set configuration values of privacyIDEA.
    """
    client = ctx.obj["pi_client"]
    for conf in config:
        param = {}
        (k, v) = conf.split("=")
        param[k] = v
        response = client.setconfig(param)
        showresult(response.data)


@config.command()
@click.pass_context
@click.option('--key', required=True, multiple=True,
              help="Delete config values from the privacyIDEA server by key.")
def delete(ctx, key):
    """
    Delete a configuration value from the privacyIDEA server.
    """
    client = ctx.obj["pi_client"]
    for k in key:
        response = client.deleteconfig(k)
        showresult(response.data)
