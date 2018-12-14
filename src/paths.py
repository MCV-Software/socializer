# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import platform
import os
import sys
#import logging
from platform_utils import paths as paths_

from functools import wraps

mode = "portable"
directory = None
fsencoding = sys.getfilesystemencoding()

#log = logging.getLogger("paths")

def app_path():
	return paths_.app_path()

def config_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory.decode(fsencoding), "config")
		elif directory == None: path = os.path.join(app_path().decode(fsencoding), "config")
	elif mode == "installed":
		path = os.path.join(data_path().decode(fsencoding), "config")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path

def logs_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory.decode(fsencoding), "logs")
		elif directory == None: path = os.path.join(app_path().decode(fsencoding), "logs")
	elif mode == "installed":
		path = os.path.join(data_path().decode(fsencoding), "logs")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path

def data_path(app_name='socializer'):
	if platform.system() == "Windows":
		data_path = os.path.join(os.getenv("AppData"), app_name)
	else:
		data_path = os.path.join(os.environ['HOME'], ".%s" % app_name)
	if not os.path.exists(data_path):
		os.mkdir(data_path)
	return data_path

def locale_path():
	return os.path.join(app_path().decode(fsencoding), "locales")

def sound_path():
	return os.path.join(app_path().decode(fsencoding), "sounds")

def com_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory.decode(fsencoding), "com_cache")
		elif directory == None: path = os.path.join(app_path().decode(fsencoding), "com_cache")
	elif mode == "installed":
		path = os.path.join(data_path().decode(fsencoding), "com_cache")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path
