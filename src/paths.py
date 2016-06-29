# -*- coding: utf-8 -*-
import platform
import os
import sys
#import logging
from platform_utils import paths as paths_

from functools import wraps

mode = "portable"
directory = None

#log = logging.getLogger("paths")

def merge_paths(func):
	@wraps(func)
	def merge_paths_wrapper(*a):
		return unicode(os.path.join(func(), *a))
	return merge_paths_wrapper

@merge_paths
def app_path():
	return paths_.app_path()

@merge_paths
def config_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory, "config")
		elif directory == None: path = app_path(u"config")
	elif mode == "installed":
		path = data_path("config")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path

@merge_paths
def logs_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory, "logs")
		elif directory == None: path = app_path(u"logs")
	elif mode == "installed":
		path = data_path("logs")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path

@merge_paths
def data_path(app_name='TW blue'):
	if platform.system() == "Windows":
		data_path = os.path.join(os.getenv("AppData"), app_name)
	else:
		data_path = os.path.join(os.environ['HOME'], ".%s" % app_name)
	if not os.path.exists(data_path):
		os.mkdir(data_path)
	return data_path

@merge_paths
def locale_path():
	return app_path(u"locales")

@merge_paths
def sound_path():
	return app_path(u"sounds")

@merge_paths
def com_path():
	global mode, directory
	if mode == "portable":
		if directory != None: path = os.path.join(directory, "com_cache")
		elif directory == None: path = app_path(u"com_cache")
	elif mode == "installed":
		path = data_path(u"com_cache")
	if not os.path.exists(path):
#		log.debug("%s path does not exist, creating..." % (path,))
		os.mkdir(path)
	return path
