#!/usr/bin/python
import keys
import logging
import vk_api_patched as vk_api
import core
from vk_api.audio import VkAudio

log = logging.getLogger("vkSessionHandler")

class vkObject(object):

	def __init__(self):
		self.api_key = keys.keyring.get_api_key()

	def login(self, user, password, token, alt_token, filename):
		if alt_token == False:
			log.info("Using kate's token...")
			if token == "" or token == None:
				log.info("Token is not valid. Generating one...")
				token = core.requestAuth(user, password)
				token = token[0]
				receipt = core.getReceipt(token)
				token = core.validateToken(token, receipt)
				log.info("Token validated...")
			self.session_object = vk_api.VkApi(app_id=self.api_key, login=user, password=password, token=token, scope="offline, wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats", config_filename=filename)
		else:
			self.session_object = vk_api.VkApi(app_id=self.api_key, login=user, password=password, scope="offline, wall, notify, friends, photos, audio, video, docs, notes, pages, status, groups, messages, notifications, stats", config_filename=filename)
			self.session_object.auth()
		self.client = self.session_object.get_api()
#		print self.client.audio.get()
		log.debug("Getting tokens for 24 hours...")
#		info = self.client.account.getProfileInfo()
		# Add session data to the application statistics.
		self.client.stats.trackVisitor()
		self.client_audio = VkAudio(self.session_object)
