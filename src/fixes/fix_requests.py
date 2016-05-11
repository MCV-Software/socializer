# -*- coding: utf-8 -*-
import requests
import paths
import os
import logging
log = logging.getLogger("fixes.fix_requests")

def fix():
	log.debug("Applying fix for requests...")
	os.environ["REQUESTS_CA_BUNDLE"] = paths.app_path("cacert.pem")
	log.debug("Changed CA path to %s" % (paths.app_path("cacert.pem"),))