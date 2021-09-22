# -*- coding: utf-8 -*-
import os
import sys
import widgetUtils
import paths
import time
import logging
import shutil
from authenticator.official import AuthenticationError
from . import wxUI as view
from . import session
from .config_utils import Configuration

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
    def __init__(self, starting=True):
        super(sessionManagerController, self).__init__()
        log.debug("Setting up the session manager.")
        if starting:
            title=_("Select an account")
        else:
            title = _("Manage accounts")
        self.view = view.sessionManagerWindow(starting=starting, title=title)
        widgetUtils.connect_event(self.view.new, widgetUtils.BUTTON_PRESSED, self.manage_new_account)
        widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.remove)
        self.fill_list()
        if len(self.sessions) == 0:
            log.debug("the session list is empty, creating a new one...")
            self.manage_new_account()

    def fill_list(self):
        self.sessions = []
        log.debug("Filling the session list...")
        for i in os.listdir(paths.config_path()):
            if i != "dicts" and os.path.isdir(os.path.join(paths.config_path(), i)):
                log.debug("Adding session %s" % (i,))
                config_test = Configuration(os.path.join(paths.config_path(), i, "session.conf"))
                name = config_test["vk"]["user"]
                if name != "" and config_test["vk"]["password"] != "":
                    self.sessions.append((i, name))
                    self.view.list.insert_item(False, *[name])

    def manage_new_account(self, *args, **kwargs):
        if view.new_account_dialog() == widgetUtils.YES:
            location = (str(time.time())[-6:])
            log.debug("Creating session in the %s path" % (location,))
            s = session.vkSession(location)
            path = os.path.join(paths.config_path(), location)
            if not os.path.exists(path):
                os.mkdir(path)
            s.get_configuration(True)
            self.get_authorisation(s)
            name = s.settings["vk"]["user"]
            self.sessions.append((location, name))
            self.view.list.insert_item(False, *[name])
            self.modified = True

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

    def do_ok(self):
        selected_session = self.sessions[self.view.list.get_selected()]
        self.session = selected_session[0]
        self.session = session.vkSession(self.session)
        self.session.get_configuration()
        session.sessions[selected_session[1]] = self.session

    def show(self):
        if len(self.sessions) > 1:
            answer = self.view.get_response()
        else:
            answer = widgetUtils.OK
        if  answer == widgetUtils.OK:
            self.do_ok()
        else:
            sys.exit()
        self.view.destroy()

    def remove(self, *args, **kwargs):
        if self.view.remove_account_dialog() == widgetUtils.YES:
            selected_session = self.sessions[self.view.list.get_selected()]
            shutil.rmtree(path=os.path.join(paths.config_path(), selected_session[0]), ignore_errors=True)
            self.sessions.remove(selected_session)
            self.view.list.remove_item(self.view.list.get_selected())
            self.modified = True
