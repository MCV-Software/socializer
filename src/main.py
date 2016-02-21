# -*- coding: utf-8 -*-
import sys
import fixes
if hasattr(sys, "frozen"):
	fixes.setup()
import platform
import languageHandler
import widgetUtils
import paths
import config
import output
import logging
import keys
import application
from mysc.thread_utils import call_threaded

log = logging.getLogger("main")

def setup():
	log.debug("Starting Socializer %s" % (application.version,))
	config.setup()
	log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
	log.debug("Application path is %s" % (paths.app_path(),))
	log.debug("config path  is %s" % (paths.config_path(),))
	output.setup()
	languageHandler.setLanguage("system")
	keys.setup()
	from controller import mainController
	from sessionmanager import sessionManager
	app = widgetUtils.mainLoopObject()
	sm = sessionManager.sessionManagerController()
	sm.fill_list()
	if len(sm.sessions) == 0: sm.show()
	else:
		sm.do_ok()
	del sm
	r = mainController.Controller()
	call_threaded(r.login)
	app.run()

setup()