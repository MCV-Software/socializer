# -*- coding: utf-8 -*-
""" this is a patched version of vk_api to  use a different user agent for authenticating against VK.
Everything else looks the same, the only change in the module is the new user agent, emulating a kate mobile session."""
import time
import hashlib
import logging
import vk_api
import threading
import requests
from authenticator.official import get_sig
from . import jconfig_patched as jconfig
from vk_api.enums import VkUserPermissions
from vk_api.exceptions import *

DEFAULT_USER_SCOPE = sum(VkUserPermissions)

class VkApi(vk_api.VkApi):

    def __init__(self, login=None, password=None, token=None, secret=None, device_id=None,
                 auth_handler=None, captcha_handler=None,
                 config=jconfig.Config, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=2685278, scope=DEFAULT_USER_SCOPE,
                 client_secret='lxhD8OD7dMsqtXIm5IUY'):

        self.login = login
        self.password = password

        self.token = {'access_token': token}
        self.secret = secret
        self.device_id = device_id
        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope
        self.client_secret = client_secret

        self.storage = config(self.login, filename=config_filename)

        self.http = requests.Session()
        self.http.headers.update({'User-agent': 'VKAndroidApp/5.23-2978 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en; 320x240)'})

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

    def method(self, method, values=None, captcha_sid=None, captcha_key=None,
               raw=False):
        """ Вызов метода API

        :param method: название метода
        :type method: str

        :param values: параметры
        :type values: dict

        :param captcha_sid: id капчи
        :type captcha_key: int or str

        :param captcha_key: ответ капчи
        :type captcha_key: str

        :param raw: при False возвращает `response['response']`
                    при True возвращает `response`
                    (может понадобиться для метода execute для получения
                    execute_errors)
        :type raw: bool
        """

        values = values.copy() if values else {}

        if 'v' not in values:
            values['v'] = self.api_version

        if self.token:
            values['access_token'] = self.token['access_token']

        if captcha_sid and captcha_key:
            values['captcha_sid'] = captcha_sid
            values['captcha_key'] = captcha_key

        with self.lock:
            # Ограничение 3 запроса в секунду
            delay = self.RPS_DELAY - (time.time() - self.last_request)

            if delay > 0:
                time.sleep(delay)
            values.update(https=1, device_id=self.device_id)
            sig = get_sig(method, values, self.secret)
            values.update(sig=sig)
            response = self.http.post(
                'https://api.vk.com/method/' + method,
                values
            )
            self.last_request = time.time()

        if response.ok:
            response = response.json()
        else:
            error = ApiHttpError(self, method, values, raw, response)
            response = self.http_handler(error)

            if response is not None:
                return response

            raise error

        if 'error' in response:
            error = ApiError(self, method, values, raw, response['error'])

            if error.code in self.error_handlers:
                if error.code == CAPTCHA_ERROR_CODE:
                    error = Captcha(
                        self,
                        error.error['captcha_sid'],
                        self.method,
                        (method,),
                        {'values': values, 'raw': raw},
                        error.error['captcha_img']
                    )

                response = self.error_handlers[error.code](error)

                if response is not None:
                    return response

            raise error

        return response if raw else response['response']
