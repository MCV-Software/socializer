# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import widgetUtils
from wxUI.dialogs import selector
from pubsub import pub
from .import base

class postInteractor(base.baseInteractor):

	def set(self, control, value):
		if not hasattr(self.view, control):
			raise AttributeError("The control is not present in the view.")
		getattr(self.view, control).SetValue(value)

	def add_tagged_users(self, users):
		self.view.text.SetValue(self.view.text.GetValue()+", ".join(users))

	def install(self, *args, **kwargs):
		super(postInteractor, self).install(*args, **kwargs)
		widgetUtils.connect_event(self.view.spellcheck, widgetUtils.BUTTON_PRESSED, self.on_spellcheck)
		widgetUtils.connect_event(self.view.translateButton, widgetUtils.BUTTON_PRESSED, self.on_translate)
		widgetUtils.connect_event(self.view.mention, widgetUtils.BUTTON_PRESSED, self.on_mention)
		if hasattr(self.view, "attach"):
			widgetUtils.connect_event(self.view.attach, widgetUtils.BUTTON_PRESSED, self.on_add_attachments)
		pub.subscribe(self.set, self.modulename+"_set")
		pub.subscribe(self.add_tagged_users, self.modulename+"_add_tagged_users")

	def uninstall(self):
		super(postInteractor, self).uninstall()
		pub.unsubscribe(self.set, self.modulename+"_set")
		pub.unsubscribe(self.add_tagged_users, self.modulename+"_add_tagged_users")

	def start(self):
		self.result = self.view.get_response()
		if self.result == widgetUtils.OK:
			self.presenter.text = self.view.get_text()
			if hasattr(self.view, "privacy"):
				self.presenter.privacy = self.get_privacy_options()
			else:
				self.presenter.privacy = 0

	def get_privacy_options(self):
		p = self.view.get("privacy")
		if p == _("Friends of friends"):
			privacy = 0
		elif p == _("All users"):
			privacy = 1
		return privacy

	def on_mention(self, *args, **kwargs):
		users = self.presenter.get_friends()
		select = selector.selectPeople(users)
		if select.get_response() == widgetUtils.OK and select.users.GetCount() > 0:
			tagged_users = select.get_all_users()
			self.presenter.add_tagged_users(tagged_users)

	def on_translate(self, *args, **kwargs):
		dlg = translator.gui.translateDialog()
		if dlg.get_response() == widgetUtils.OK:
			text_to_translate = self.message.get_text()
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			self.presenter.translate(text_to_translate, dest)
		dlg.Destroy()

	def on_spellcheck(self, event=None):
		text = self.message.get_text()
		self.presenter.spellcheck(text)

	def on_add_attachments(self, *args, **kwargs):
		self.presenter.add_attachments()