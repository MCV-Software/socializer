# -*- coding: utf-8 -*-
import threading
from vk import longpool
from pubsub import pub
from logging import getLogger
log = getLogger("controller.longpolThread")

class worker(threading.Thread):
	def __init__(self, session):
		super(worker, self).__init__()
		log.debug("Instanciating longPoll server")
		self.session = session
		self.l =  longpool.LongPoll(self.session.vk.client)

	def run(self):
		while self.session.is_logged == True:
			log.debug("Calling to check...")
			p = self.l.check()
#			log.debug("check has returned " + p)
			for i in p:
#				print i.message_id, i.flags, i.from_id, i.user_id, i.mask, i.byself, i.message_flags
#				if i.flags == 4 or i.flags == 51 or i.flags == 49:
				if i.text != None and i.from_id != None and i.flags != None and i.message_flags != None:
#					print i.message_id, i.flags, i.from_id, i.user_id, i.mask, i.byself, i.message_flags
#					if i.from_id != None:
#					print "ordering sent stuff"
					pub.sendMessage("order-sent-message", obj=i)
