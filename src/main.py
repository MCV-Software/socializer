# -*- coding: utf-8 -*-
import logger
import sys
import fixes
import traceback
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
sys.excepthook = lambda x, y, z: logging.critical(''.join(traceback.format_exception(x, y, z)))
from mysc.thread_utils import call_threaded

log = logging.getLogger("main")

def setup():
	log.debug("Starting Socializer %s" % (application.version,))
	config.setup()
	log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
	log.debug("Application path is %s" % (paths.app_path(),))
	log.debug("config path  is %s" % (paths.config_path(),))
	output.setup()
	languageHandler.setLanguage(config.app["app-settings"]["language"])
	log.debug("Language set to %s" % (languageHandler.getLanguage()))
	keys.setup()
	from controller import mainController
	from sessionmanager import sessionManager
	app = widgetUtils.mainLoopObject()
	log.debug("Created Application mainloop object")
	sm = sessionManager.sessionManagerController()
	del sm
	r = mainController.Controller()
	call_threaded(r.login)
	app.run()

setup()
