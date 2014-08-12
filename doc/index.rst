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
    * machine: machine commands used to create new machines and assign tokens and applications to these machines
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


