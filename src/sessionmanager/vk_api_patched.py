# -*- coding: utf-8 -*-
""" this is a patched version of vk_api to  use a different user agent for authenticating against VK.
Everything else looks the same, the only change in the module is the new user agent, emulating a kate mobile session."""
import logging
import vk_api
import threading
import requests
import jconfig
from vk_api.enums import VkUserPermissions
from vk_api.exceptions import *

DEFAULT_USER_SCOPE = sum(VkUserPermissions)

class VkApi(vk_api.VkApi):

    def __init__(self, login=None, password=None, token=None,
                 auth_handler=None, captcha_handler=None,
                 config=jconfig.Config, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=6222115, scope=DEFAULT_USER_SCOPE,
                 client_secret=None):

        self.login = login
        self.password = password

        self.token = {'access_token': token}

        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope
        self.client_secret = client_secret

        self.storage = config(self.login, filename=config_filename)

        self.http = requests.Session()
        self.http.headers.update({'User-agent': 'KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)'})

        self.last_request = 0.0

        self.error_handlers = {
            NEED_VALIDATION_CODE: self.need_validation_handler,
            CAPTCHA_ERROR_CODE: captcha_handler or self.captcha_handler,
            TOO_MANY_RPS_CODE: self.too_many_rps_handler,
            TWOFACTOR_CODE: auth_handler or self.auth_handler
        }

        self.lock = threading.Lock()

        self.logger = logging.getLogger('vk_api_patched')
        self.logger.info('Started patched VK API client...')