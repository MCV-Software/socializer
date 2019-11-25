#! /usr/bin/env python
""" Upload socializer to the ftp server. """
import sys
import os
import glob
import ftplib

transferred=0

def convert_bytes(n):
 K, M, G, T, P = 1 << 10, 1 << 20, 1 << 30, 1 << 40, 1 << 50
 if   n >= P:
  return '%.2fPb' % (float(n) / T)
 elif   n >= T:
  return '%.2fTb' % (float(n) / T)
 elif n >= G:
  return '%.2fGb' % (float(n) / G)
 elif n >= M:
  return '%.2fMb' % (float(n) / M)
 elif n >= K:
  return '%.2fKb' % (float(n) / K)
 else:
  return '%d' % n

def callback(progress):
	global transferred
	transferred = transferred+len(progress)
	print("Uploaded {}".format(convert_bytes(transferred),))

ftp_server = os.environ.get("FTP_SERVER") or sys.argv[1]
ftp_username = os.environ.get("FTP_USERNAME") or sys.argv[2]
ftp_password = os.environ.get("FTP_PASSWORD") or sys.argv[3]
version = os.environ.get("CI_COMMIT_TAG") or sys.argv[4]
version = version.replace("v", "")

print("Uploading files to the Socializer server...")
connection = ftplib.FTP(ftp_server)
print("Connected to FTP server {}".format(ftp_server,))
connection.login(user=ftp_username, passwd=ftp_password)
print("Logged in successfully")
connection.cwd("static/files/")
if version not in connection.nlst():
	print("Creating version directory {} because does not exists...".format(version,))
	connection.mkd(version)
connection.cwd(version)
print("Moved into version directory")
files = glob.glob("*.zip")+glob.glob("*.exe")
print("These files will be uploaded into the version folder: {}".format(files,))
for file in files:
	transferred = 0
	print("Uploading {}".format(file,))
	with open(file, "rb") as f:
		connection.storbinary('STOR %s' % file, f, callback=callback, blocksize=1024*1024) 
print("Upload completed. exiting...")
connection.quit()