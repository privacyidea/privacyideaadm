.. privacyidea documentation master file, created by
   sphinx-quickstart on Tue Aug 12 15:34:53 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to privacyidea's documentation!
=======================================

SYNOPSIS
--------

privacyidea -U URL -a ADMIN [-p PASSWORD] COMMMAND <COMMAND-OPTIONS>


DESCRIPTON
----------
This is the command line tool for the privacyIDEA server. It can be used to do
several special actions like 

 * enrolling tokens, 
 * listing users and tokens,
 * assign and delete tokens, 
 * create and manage machines etc. 

You can put parameters like the password or the host connection definition into a file
like 'my-secret-connection-values.txt' and reference this file like this at
the command line: 

@my-secret-connection-values.txt 

Thus you can use the command line tool to perform automatic tasks and avoid exposing
secret credentials in the process list.

OPTIONS
-------
  -h, --help            show this help message and exit
  -U URL, --url URL     The URL of the privacyIDEA server including protocol
                        and port like https://localhost:5001
  -a ADMIN, --admin ADMIN
                        The name of the administrator like admin@admin
  -p PASSWORD, --password PASSWORD
                        The password of the administrator. Please avoid to
                        post the password at the command line. You will be
                        asked for it - or you can provide the password in a
                        configuration file. Note, that you can write a file
                        password.txt containing two lines '--password' and the
                        second line the password itself and add this to the
                        command line with @password.txt
  -v, --version         Print the version of the program.

COMMANDS
--------
  The command line tool requires commands, to know what action it should
  take. Some commands have only one level, other commands are grouped and
  have two levels.

  You can get help at each level by appending the parameter -h.

  Top level commands are:

    * user: list the available users.
    * token: token commands used to list tokens, assign, enroll, resync ...
    * machine: machine commands used to list machines and assign tokens and
    applications to these machines
    * securitymodule: Get the status of the securitymodule or set the password of the securitymodule
    * config: server configuration
    * realm: realm configuration
    * resolver: resolver configuration

EXAMPLES
--------

Enroll a Yubikey in challenge response mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
   privacyidea @secrets.txt token yubikey_mass_enroll --yubiCR --yubislot 2

This will enroll the Yubikey in challenge response mode and the C/R will
be written to slot 2. Thus the yubikey can be used for LUKS.

The file `secrets.txt` would look like this::
   
   --password
   topSecr3t
   --url
   https://your-server:443
   --admin
   admin@admin


Get the Authentication Items from a Yubikey in challenge Response mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You have assigned the above enrolled Yubikey to a machine with the LUKS
application. You can then get the authentication item like this::

   privacyidea @secrets machine authitem --hostname <machine>
   Please enter password for 'admin':

    {   u'status': True,
        u'value': {   u'luks': [   {   u'challenge': u'43eca67a4cf12a1b158c4ec7c1100b7529fb3f3d19370c040320c2245a4ae91d',
                                       u'partition': u'/dev/sda',
                                       u'response': u'1636b930f3ee4b37b8fe0cd9f979bb9fc99cd3ed',
                                       u'slot': u'1'}]}}

This means the **challenge** sent to the Yubikey will always produce the
mentioned **response**.

This can be used to populate an LUKS slot.

To verify this use the command::

   ykchalresp 43eca67a4cf12a1b158c4ec7c1100b7529fb3f3d19370c040320c2245a4ae91d

Enroll an eToken NG OTP under Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You need the SafeNet Authentication Client (driver/middleware) to enroll the eToken NG.
Please ensure, that you have installed it.

.. note:: You should have administrative rights, when enrolling the eToken NG.

.. note:: If you are experiencing problems like "ET_TokenInitFinal failed", you
   should install the eToken PKI Client 5.1 SP1.

Now you need to install Python for Windows 2.7.8. You can get this from
https://www.python.org/downloads/release/.

This will be installed to C:\python27 by default.

You need an additional python module ``usb``, which you can get here:
http://sourceforge.net/projects/pyusb/files/PyUSB%201.0/1.0.0-beta-2/pyusb-1.0.0b2.zip/download

Please unpack it and from within the new folder issue the following commands::
   
   c:\python27\python setup.py build
   c:\python27\python setup.py install

Now you need to unpack the latest privacyideaadm package and also install it via the
same commands `setup.py build` and `install` as above.

The scripts are installed to `C:\python27\scripts`.

Now you can start the command line client to enroll eToken NG::

   c:\python27\python c:\python27\python\scripts\privacyidea \
   -U https://server
   -a admin@admin token etokenng_mass_enroll

