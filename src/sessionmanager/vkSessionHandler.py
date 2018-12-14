#!/usr/bin/python
import keys
import logging
import vk_api
import core
from vk_api.audio import VkAudio
import core
log = logging.getLogger("vkSessionHandler")

class vkObject(object):

	def __init__(self):
		self.api_key = keys.keyring.get_api_key()

	def login(self, user, password, filename):
		log.debug("Logging in vk using user/password authentication")
#		token = core.requestAuth(user, password)
		self.session_object = vk_api.VkApi(app_id=self.api_key, login=user, password=password, scope="offline, wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats", config_filename=filename)
		self.session_object.auth(token_only=True)
		self.client = self.session_object.get_api()
#		self.client = API(s, v=self.api_version)
		log.debug("Getting tokens for 24 hours...")
#		info = self.client.account.getProfileInfo()
		# Add session data to the application statistics.
		self.client.stats.trackVisitor()
		self.client_audio = VkAudio(self.session_object)
