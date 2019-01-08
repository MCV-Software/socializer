# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import views
import interactors
import output
from logging import getLogger
from pubsub import pub
from extra import SpellChecker, translator
from .import attach
from .import base

log = getLogger("controller.message")

class createPostPresenter(base.basePresenter):

	def __init__(self, session, view, interactor):
		super(createPostPresenter, self).__init__(view=view, interactor=interactor, modulename="create_post")
		self.session = session
		self.images = []
		self.tagged_people = []
		self.run()

	def get_friends(self):
		try:
			fields = "id, first_name, last_name"
			self.friends = self.session.vk.client.friends.get(count=5000, fields=fields)
		except AttributeError:
			time.sleep(2)
			log.exception("Error retrieving friends...")
			return []
		self.users = []
		for i in self.friends["items"]:
			self.users.append("{0} {1}".format(i["first_name"], i["last_name"]))
		return self.users

	def add_tagged_users(self, tagged_users):
		self.tagged_people = []
		for i in tagged_users:
			self.tagged_people.append("[id%s|%s]" % (str(self.friends["items"][i]["id"]), self.friends["items"][i]["first_name"]))
		self.send_message("add_tagged_users", users=self.tagged_people)

	def translate(self, text, language):
		msg = translator.translator.translate(text, language)
		self.send_message("set", control="text", value=msg)
		self.send_message("focus_control", control="text")
		output.speak(_("Translated"))

	def spellcheck(self, text):
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.send_message("set", control="text", value=checker.fixed_text)
			self.send_message("focus_control", control="text")
		checker.clean()

	def add_attachments(self):
		a = attach.attachPresenter(session=self.session, view=views.attachDialog(), interactor=interactors.attachInteractor())
		if len(a.attachments) != 0:
			self.attachments = a.attachments
