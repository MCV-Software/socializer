# -*- coding: utf-8 -*-
import logging
log = logging.getLogger("keyring")

keyring = None

def setup():
    global keyring
    if keyring == None:
        keyring = Keyring()
        log.debug("Keyring started")

class Keyring(object):

    def get_api_key(self):
        return "5093442"
