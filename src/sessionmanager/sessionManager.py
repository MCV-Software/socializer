# -*- coding: utf-8 -*-
import os
import sys
import widgetUtils
import paths
import time
import logging
from authenticator.official import AuthenticationError
from . import wxUI as view
from . import session
from .config_utils import Configuration

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
	def __init__(self):
		super(sessionManagerController, self).__init__()
		log.debug("Setting up the session manager.")
		self.fill_list()
		if not hasattr(self, "session"):
			log.debug("the session list is empty, creating a new one...")
			self.manage_new_account()

	def fill_list(self):
		log.debug("Filling the session list...")
		for i in os.listdir(paths.config_path()):
			if os.path.isdir(os.path.join(paths.config_path(), i)):
				log.debug("Adding session %s" % (i,))
				config_test = Configuration(os.path.join(paths.config_path(), i, "session.conf"))
				name = config_test["vk"]["user"]
				if name != "" and config_test["vk"]["password"] != "":
					self.session = i
					s = session.vkSession(self.session)
					s.get_configuration()
					session.sessions[self.session] = s

	def manage_new_account(self):
		if view.new_account_dialog() == widgetUtils.YES:
			location = (str(time.time())[-6:])
			log.debug("Creating session in the %s path" % (location,))
			s = session.vkSession(location)
			path = os.path.join(paths.config_path(), location)
			if not os.path.exists(path):
				os.mkdir(path)
			s.get_configuration()
			self.get_authorisation(s)
			session.sessions[location] = s
		else:
			sys.exit()

	def get_authorisation(self, c):
		log.debug("Starting the authorisation process...")
		dl = view.newSessionDialog()
		if dl.ShowModal() == widgetUtils.OK:
			c.settings["vk"]["user"] = dl.get_email()
			c.settings["vk"]["password"] = dl.get_password()
			try:
				c.login()
			except AuthenticationError:
				c.settings["vk"]["password"] = ""
				c.settings["vk"]["user"]
				return self.get_authorisation(c)