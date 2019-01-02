# -*- coding: utf-8 -*-
import application
import platform
import logging
import output
from requests.exceptions import ConnectionError
from . import update
from .wxUpdater import *
logger = logging.getLogger("updater")

def do_update(update_type="stable"):
 if update_type == "stable":
  endpoint = application.update_stable_url
  version = application.version
 else:
  endpoint = application.update_next_url
  version = application.update_next_version
 try:
  return update.perform_update(endpoint=endpoint, current_version=version, app_name=application.name, update_type=update_type, update_available_callback=available_update_dialog, progress_callback=progress_callback, update_complete_callback=update_finished)
 except ConnectionError:
  logger.exception("Update failed.")
  output.speak("An exception occurred while attempting to update " + application.name + ". If this message persists, contact the " + application.name + " developers. More information about the exception has been written to the error log.",True)