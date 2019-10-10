# -*- coding: utf-8 -*-
import threading
from pubsub import pub
from . import base

class blacklistPresenter(base.basePresenter):

	def __init__(self, session, view, interactor):
		self.session = session
		super(blacklistPresenter, self).__init__(view=view, interactor=interactor, modulename="blacklist")
		self.worker = threading.Thread(target=self.load_information)
		self.worker.finished = threading.Event()
		self.worker.start()
		self.run()

	def load_information(self):
		banned_users = self.session.vk.client.account.getBanned(count=200)
		self.users = banned_users["profiles"]
		items = []
		for i in self.users:
			str_user = "{first_name} {last_name}".format(first_name=i["first_name"], last_name=i["last_name"])
			items.append([str_user])
		self.send_message("add_items", control="persons", items=items)

	def unblock_person(self, item):
		result = self.session.vk.client.account.unban(owner_id=self.users[item]["id"])
		if result == 1:
			msg = _("You've unblocked {user1_nom} from your friends.").format(**self.session.get_user(self.users[item]["id"]),)
			pub.sendMessage("notify", message=msg)
		return result