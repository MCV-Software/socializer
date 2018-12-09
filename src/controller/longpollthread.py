# -*- coding: utf-8 -*-
import threading
from vk_api.longpoll import VkLongPoll, VkEventType
from pubsub import pub
from logging import getLogger
log = getLogger("controller.longpolThread")

class worker(threading.Thread):
	def __init__(self, session):
		super(worker, self).__init__()
		log.debug("Instantiating longPoll server")
		self.session = session
		self.longpoll = VkLongPoll(self.session.vk.session_object)

	def run(self):
		print("starting events")
		for event in self.longpoll.listen():
			print(event)
			if event.type == VkEventType.MESSAGE_NEW:
				pub.sendMessage("order-sent-message", obj=event)
			elif event.type == VkEventType.USER_ONLINE:
				print "User online"
				print event.user_id
			elif event.type == VkEventType.USER_OFFLINE:
				print "User offline"
				print  event.user_id