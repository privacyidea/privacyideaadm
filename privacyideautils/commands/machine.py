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

KNOWN_APPS = ["ssh", "luks", "offline"]


def options_to_dict(Option):
    '''
    This takes an array Option consisting of entries like
    slot=7, partition=dev3
    and converts it to a dictionary:
    { "option_slot": "7",
      "option_partition": "dev3" }

    :param Option: array of options
    :type Option: array
    :return: dictionary
    '''
    options = {}
    for option in Option:
        opt = option.split("=")
        if len(opt) == 2:
            # There was exactly one equal sign and we have a key and a value
            value = opt[1]
            if opt[0].startswith("option_"):
                key = opt[0]
            else:
                key = "option_" + opt[0]
            options[key] = value
    return options


@click.group()
@click.pass_context
def machine(ctx):
    """
    Machine commands used to list machines
    and assign tokens and applications to these machines.
    """
    pass


@machine.command()
@click.pass_context
def list(ctx):
    """
    List the machines found in the machine resolvers.
    """
    client = ctx.obj["pi_client"]
    response = client.get('/machine/')
    showresult(response.data)


@machine.command()
@click.pass_context
@click.option("--hostname", help="List the attached tokens of this machine.")
@click.option("--serial", help="List the attachments for this token.")
@click.option("--machineid", help="List the attachments for this machine ID.")
@click.option("--resolver", help="List the machines in this machine resolver.")
def listtoken(ctx, hostname, serial, machineid, resolver):
    """
    List the token machine mapping.
    You can list all mappings for a token, for a machine or all machines in
    a machine resolver.
    """
    client = ctx.obj["pi_client"]
    param = {}
    if hostname:
        param["hostname"] = hostname
    if serial:
        param["serial"] = serial
    if machineid:
        param["machineid"] = machineid
    if resolver:
        param["resolver"] = resolver
    response = client.get("/machine/token", param)
    showresult(response.data)


@machine.command()
@click.pass_context
@click.option("--hostname", required=True,
              help="The hostname of the machine, for which the authitem should be retrieved.")
@click.option("--application",
              help="The application, which authitems should be retrieved.")
@click.option("--challenge",
              help="If the application requires a challenge, you can pass a challenge, for"
                   " which the authitem will be returned.")
def authitem(ctx, application, hostname, challenge):
    """
    Get the authentication item for the given machine and application.
    """
    client = ctx.obj["pi_client"]
    param = {}
    if application:
        param["application"] = application
    if hostname:
        param["hostname"] = hostname
    if challenge:
        param["challenge"] = challenge
    if param.get("application"):
        response = client.get("/machine/authitem/%s" % param.get(
            "application"), param)
    else:
        response = client.get("/machine/authitem", param)
    showresult(response.data)


@machine.command()
@click.pass_context
@click.option("--hostname", help="The hostname of the machine", required=True)
@click.option("--serial", required=True, help="The serial of the token.")
@click.option("--application", required=True, help="The application type to attach.",
              type=click.Choice(KNOWN_APPS))
@click.option("--option", help="Option for the application, like key=value.", multiple=True)
def attach(ctx, hostname, serial, application, option):
    """
    Attach a token with an application to a machine
    """
    client = ctx.obj["pi_client"]
    param = {"name": hostname,
             "serial": serial,
             "application": application}
    ret = client.post("/machine/token", param)
    showresult(ret)
    if len(option) > 0:
        options = options_to_dict(option)
        param.update(options)
        ret = client.post("/machine/tokenoption", param)
        showresult(ret)


@machine.command()
@click.pass_context
@click.option("--hostname", help="The hostname of the machine", required=True)
@click.option("--serial", required=True, help="The serial of the token.")
@click.option("--application", required=True, help="The application type to attach.",
              type=click.Choice(KNOWN_APPS))
def detach(ctx, hostname, serial, application):
    """
    Detach a token from a machine.
    """
    client = ctx.obj["pi_client"]
    ret = client.post("/machine/deltoken",
                         {"name": hostname,
                          "serial": serial,
                          "application": application})
    showresult(ret)


@machine.command()
@click.pass_context
@click.option("--hostname", help="The hostname of the machine", required=True)
@click.option("--serial", required=True, help="The serial of the token.")
@click.option("--application", required=True, help="The application type to attach.",
              type=click.Choice(KNOWN_APPS))
@click.option("--option", help="Option for the application, like key=value.", multiple=True)
def add_option(ctx, hostname, serial, application, option):
    """
    Add options to an attached token
    """
    client = ctx.obj["pi_client"]
    param = {"name": hostname,
             "serial": serial,
             "application": application}
    if len(args.option) > 0:
        options = options_to_dict(option)
        param.update(options)
        ret = client.post("/machine/tokenoption", param)
        showresult(ret)


@machine.command()
@click.pass_context
@click.option("--hostname", help="The hostname of the machine", required=True)
@click.option("--serial", required=True, help="The serial of the token.")
@click.option("--application", required=True, help="The application type to attach.",
              type=click.Choice(KNOWN_APPS))
@click.option("--option", help="Option for the application, like key=value.", multiple=True)
def delete_option(ctx, hostname, serial, application, option):
    """
    Delete options from an attached token
    """
    client = ctx.obj["pi_client"]
    param = {"name": hostname,
             "serial": serial,
             "application": application}
    if len(args.option) > 0:
        options = options_to_dict(option)
        for k in options.keys():
            param["key"] = k
            ret = client.post("/machine/deloption", param)
            showresult(ret)
