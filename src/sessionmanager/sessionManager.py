# -*- coding: utf-8 -*-
import os
import shutil
import widgetUtils
import wxUI as view
import paths
import time
import os
import logging
import session
from config_utils import Configuration

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
	def __init__(self):
		super(sessionManagerController, self).__init__()
		log.debug("Setting up the session manager.")
		self.view = view.sessionManagerWindow()
		widgetUtils.connect_event(self.view.new, widgetUtils.BUTTON_PRESSED, self.manage_new_account)
		widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.remove)
		self.new_sessions = {}
		self.removed_sessions = []

	def fill_list(self):
		sessionsList = []
		log.debug("Filling the sessions list.")
		self.sessions = []
		for i in os.listdir(paths.config_path()):
			if os.path.isdir(paths.config_path(i)):
				log.debug("Adding session %s" % (i,))
				strconfig = "%s/session.conf" % (paths.config_path(i))
				config_test = Configuration(strconfig)
				name = config_test["vk"]["user"]
				sessionsList.append(name)
				self.sessions.append(i)
		self.view.fill_list(sessionsList)

	def show(self):
		if self.view.get_response() == widgetUtils.OK:
			self.do_ok()

	def do_ok(self):
		log.debug("Starting sessions...")
		for i in self.sessions:
			if session.sessions.has_key(i) == True: continue
			s = session.vkSession(i)
			s.get_configuration()
			session.sessions[i] = s
			self.new_sessions[i] = s

	def manage_new_account(self, *args, **kwargs):
		if self.view.new_account_dialog() == widgetUtils.YES:
			location = (str(time.time())[-6:])
			log.debug("Creating session in the %s path" % (location,))
			s = session.vkSession(location)
			path = paths.config_path(location)
			if not os.path.exists(path):
				log.debug("Creating %s path" % (paths.config_path(path),))
				os.mkdir(path)
			s.get_configuration()
			self.get_authorisation(s)
			self.sessions.append(location)
			self.view.add_new_session_to_list()
#   except:
#    log.exception("Error authorising the session")
#    self.view.show_unauthorised_error()
#    return

	def remove(self, *args, **kwargs):
		if self.view.remove_account_dialog() == widgetUtils.YES:
			selected_account = self.sessions[self.view.get_selected()]
			self.view.remove_session(self.view.get_selected())
			self.removed_sessions.append(selected_account)
			self.sessions.remove(selected_account)
			shutil.rmtree(path=paths.config_path(selected_account), ignore_errors=True)

	def get_authorisation(self, c):
		dl = view.newSessionDialog()
		if dl.ShowModal() == widgetUtils.OK:
			c.settings["vk"]["user"] = dl.get_email()
			c.settings["vk"]["password"] = dl.get_password()
			c.authorise()
			c.settings.write()
