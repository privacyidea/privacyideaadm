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
def audit(ctx):
    """
    Manage the audit log. Basically fetch audit information.
    """
    pass


@audit.command()
@click.pass_context
@click.option("--page", help="The page number to view", type=int)
@click.option("--rp", help="The number of entries per page", type=int)
@click.option("--sortname", help="The name of the column to sort by", default="number")
@click.option("--sortorder", help="The order to sort (desc, asc)",
              type=click.Choice(["desc", "asc"]), default="desc")
@click.option("--query", help="A search tearm to search for")
@click.option("--qtype", help="The column to search for")
def list(ctx, page, rp, sortname, sortorder, query, qtype):
    """
    List the audit log
    """
    client = ctx.obj["pi_client"]
    param = {}
    if page:
        param["page"] = page
    if rp:
        param["rp"] = rp
    if sortname:
        param["sortname"] = sortname
    if sortorder:
        param["sortorder"] = sortorder
    if query:
        param["query"] = query
    if qtype:
        param["qtype"] = qtype
    resp = client.auditsearch(param)
    r1 = resp.data
    auditdata = r1.get("result").get("value").get("auditdata")
    count = r1.get("result").get("value").get("count")
    for row in auditdata:
        print(row)
    print("Total: {0!s}".format(count))
