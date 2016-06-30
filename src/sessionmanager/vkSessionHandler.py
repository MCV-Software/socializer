#!/usr/bin/python
import keys
import logging
from vk import API, AuthSession, Session
log = logging.getLogger("vkSessionHandler")

class vkObject(object):

	def __init__(self):
		self.api_key = keys.keyring.get_api_key()
		self.api_version = 5.52
		log.debug("Created vkSession using VK API Version %s" % (self.api_version,))

	def login(self, user, password):
		log.debug("Logging in vk using user/password authentication")
		s = AuthSession(app_id=self.api_key, user_login=user, user_password=password, scope="wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats")
		self.client = API(s, v=self.api_version)
		log.debug("Getting tokens for 24 hours...")
		self.client.account.getProfileInfo()

	def login_access_token(self, token):
		log.debug("Logging in VK using stored tokens...")
		s = Session(access_token=token)
		self.client = API(s, v=self.api_version)
		return self.client.account.getProfileInfo()