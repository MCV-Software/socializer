#!/usr/bin/python
import keys
import logging
import vk_api
from vk_api.audio import VkAudio
log = logging.getLogger("vkSessionHandler")

class vkObject(object):

	def __init__(self):
		self.api_key = keys.keyring.get_api_key()

	def login(self, user, password):
		log.debug("Logging in vk using user/password authentication")
		self.session_object = vk_api.VkApi(app_id=self.api_key, login=user, password=password, scope="wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats")
		self.session_object.auth()
		self.client = self.session_object.get_api()
#		self.client = API(s, v=self.api_version)
		log.debug("Getting tokens for 24 hours...")
		self.client.account.getProfileInfo()
		# Add session data to the application statistics.
		self.client.stats.trackVisitor()
		self.client_audio = VkAudio(self.session_object)

	def login_access_token(self, token):
		log.debug("Logging in VK using stored tokens...")
		self.session_object = vk_api.VkApi(app_id=self.api_key, token=token, scope="wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats")
		self.session_object.auth()
		self.client = self.session_object.get_api()
		self.client_audio = VkAudio(self.session_object)
		return self.client.account.getProfileInfo()