# -*- coding: utf-8 -*-
import requests
import paths
import os
import logging
log = logging.getLogger("fixes.fix_requests")

def fix():
	log.debug("Applying fix for requests...")
	os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(paths.app_path().decode(paths.fsencoding), "cacert.pem").encode(paths.fsencoding)
	log.debug("Changed CA path to %s" % (os.environ["REQUESTS_CA_BUNDLE"].decode(paths.fsencoding)))