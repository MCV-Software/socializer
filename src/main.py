# -*- coding: utf-8 -*-
import logger
import sys
import fixes
import traceback
#if hasattr(sys, "frozen"):
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
#sys.excepthook = lambda x, y, z: logging.critical(''.join(traceback.format_exception(x, y, z)))
from mysc.thread_utils import call_threaded
from wxUI import commonMessages

log = logging.getLogger("main")

orig_session_init = None

def setup():
	global orig_session_init
	log.debug("Starting Socializer %s" % (application.version,))
	config.setup()
	log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
	log.debug("Application path is %s" % (paths.app_path(),))
	log.debug("config path  is %s" % (paths.config_path(),))
	output.setup()
	languageHandler.setLanguage(config.app["app-settings"]["language"])
	log.debug("Language set to %s" % (languageHandler.getLanguage()))
	keys.setup()
	app = widgetUtils.mainLoopObject()
	if config.app["app-settings"]["first_start"]:
		proxy_option = commonMessages.proxy_question()
		if proxy_option == widgetUtils.YES:
			config.app["app-settings"]["use_proxy"] = True
			config.app["app-settings"]["first_start"] = False
			config.app.write()
	if config.app["app-settings"]["use_proxy"]:
		log.debug("Enabling proxy support... ")
		import requests
		orig_session_init=requests.sessions.Session.__init__
		requests.sessions.Session.__init__=patched_session_init
		requests.Session.__init__=patched_session_init
	from controller import mainController
	from sessionmanager import sessionManager

	log.debug("Created Application mainloop object")
	sm = sessionManager.sessionManagerController()
	del sm
	r = mainController.Controller()
	call_threaded(r.login)
	app.run()

def patched_session_init(self):
	global orig_session_init
	orig_session_init(self)
	self.proxies={"http": "http://socializer:socializer@socializer.su:3128",
	"https": "http://socializer:socializer@socializer.su:3128"}

setup()
