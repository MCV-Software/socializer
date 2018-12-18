# -*- coding: utf-8 -*-
import threading
from vk_api.longpoll import VkLongPoll, VkEventType
from pubsub import pub
from requests.exceptions import ReadTimeout, ConnectionError

from logging import getLogger
log = getLogger("controller.longpolThread")

class worker(threading.Thread):
	def __init__(self, session):
		super(worker, self).__init__()
		log.debug("Instantiating longPoll server")
		self.session = session
		self.longpoll = VkLongPoll(self.session.vk.session_object)

	def run(self):
		try:
			for event in self.longpoll.listen():
				if event.type == VkEventType.MESSAGE_NEW:
					pub.sendMessage("order-sent-message", obj=event)
				elif event.type == VkEventType.USER_ONLINE:
					pub.sendMessage("user-online", event=event)
				elif event.type == VkEventType.USER_OFFLINE:
					pub.sendMessage("user-offline", event=event)
		except ReadTimeout, ConnectionError:
			pub.sendMessage("longpoll-read-timeout")