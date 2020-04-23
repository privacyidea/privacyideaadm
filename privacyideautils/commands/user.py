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
def user(ctx):
    """
    Manage users.
    """
    pass


@user.command()
@click.pass_context
def list(ctx):
    """
    List all available users
    """
    client = ctx.obj["pi_client"]
    resp = client.userlist({'username': '*'})
    r1 = resp.data
    result = r1['result']
    tabentry = ['username',
                'surname',
                'userid',
                'phone',
                'mobile',
                'email']
    tabsize = [20, 20, 20, 20, 20, 20]
    tabstr = ["%20s", "%20s", "%20s", "%20s", "%20s", "%20s"]
    tabdelim = '|'
    tabvisible = [0, 1, 2, 3, 4, 5]
    tabhead = ['login', 'surname', 'Id', 'phone', 'mobile', 'email']
    dumpresult(result['status'],
               result['value'],
               {'tabsize': tabsize, 'tabstr': tabstr,
                'tabdelim': tabdelim, 'tabvisible': tabvisible,
                'tabhead': tabhead, 'tabentry': tabentry})
