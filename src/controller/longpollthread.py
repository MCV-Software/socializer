# -*- coding: utf-8 -*-
import threading
from mysc import longpoll
from pubsub import pub
from logging import getLogger
log = getLogger("controller.longpolThread")

class worker(threading.Thread):
	def __init__(self, session):
		super(worker, self).__init__()
		log.debug("Instanciating longPoll server")
		self.session = session
		self.l =  longpoll.LongPoll(self.session.vk.client)

	def run(self):
		while self.session.is_logged == True:
			log.debug("Calling to check...")
			p = self.l.check()
#			log.debug("check has returned " + p)
			for i in p:
				if i.text != None and i.from_id != None and i.flags != None and i.message_flags != None:
					pub.sendMessage("order-sent-message", obj=i)
