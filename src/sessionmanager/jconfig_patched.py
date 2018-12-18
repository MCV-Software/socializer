# -*- coding: utf-8 -*-
""" Modified Jconfig base class """
import logging
import json
from codecs import open
from jconfig import jconfig

log = logging.getLogger('jconfig_patched')

class Config(jconfig.Config):

    log.info("Instantiated patched jconfig instance")

    def load(self, filename, **kwargs):
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                settings = json.load(f)
        except (IOError, ValueError):
            settings = {}

        settings.setdefault(self.section_name, {})

        return settings

    def save(self):
        with open(self._filename, 'w', encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, sort_keys=True)
