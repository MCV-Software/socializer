# -*- coding: utf-8 -*-
import os
import sys
import widgetUtils
import wxUI as view
import paths
import time
import logging
import session
from config_utils import Configuration

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
	def __init__(self):
		super(sessionManagerController, self).__init__()
		log.debug("Setting up the session manager.")
		self.fill_list()
		if not hasattr(self, "session"):
			self.manage_new_account()

	def fill_list(self):
		for i in os.listdir(paths.config_path()):
			if os.path.isdir(paths.config_path(i)):
				log.debug("Adding session %s" % (i,))
				strconfig = "%s/session.conf" % (paths.config_path(i))
				config_test = Configuration(strconfig)
				name = config_test["vk"]["user"]
				self.session = i
				s = session.vkSession(self.session)
				s.get_configuration()
				session.sessions[self.session] = s

	def manage_new_account(self):
		if view.new_account_dialog() == widgetUtils.YES:
			location = (str(time.time())[-6:])
			log.debug("Creating session in the %s path" % (location,))
			s = session.vkSession(location)
			path = paths.config_path(location)
			if not os.path.exists(path):
				log.debug("Creating %s path" % (paths.config_path(path),))
				os.mkdir(path)
			s.get_configuration()
			self.get_authorisation(s)
			session.sessions[location] = s
		else:
			sys.exit()

	def get_authorisation(self, c):
		dl = view.newSessionDialog()
		if dl.ShowModal() == widgetUtils.OK:
			c.settings["vk"]["user"] = dl.get_email()
			c.settings["vk"]["password"] = dl.get_password()
			c.settings.write()
