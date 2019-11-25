#! /usr/bin/env python
""" Upload socializer to the ftp server. """
import os
import sys
import ftplib

ftp_server = sys.argv[1]
ftp_username = sys.argv[2]
ftp_password = sys.argv[2]
source_file = sys.argv[3]
dest_file = sys.argv[4]
version = sys.argv[5]
