# -*- coding: utf-8 -*-
import time
import widgetUtils
import output
from pubsub import pub
import attach
from wxUI.dialogs import message, selector
from extra import SpellChecker, translator
from logging import getLogger

log = getLogger("controller.message")

class post(object):
	def __init__(self, session, title, caption, text, post_type="post"):
		super(post, self).__init__()
		self.session = session
		self.title = title
		self.message = getattr(message, post_type)(title, caption, text)
		self.message.set_title(title)
		widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
		widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
		widgetUtils.connect_event(self.message.mention, widgetUtils.BUTTON_PRESSED, self.mention)
		self.images = []
		if hasattr(self.message, "attach"):
			widgetUtils.connect_event(self.message.attach, widgetUtils.BUTTON_PRESSED, self.show_attach_dialog)

	def get_privacy_options(self):
		p = self.message.get("privacy")
		if p == _(u"Friends of friends"):
			privacy = 0
		elif p == _(u"All users"):
			privacy = 1
		return privacy

	def mention(self, *args, **kwargs):
		try:
			fields = "id, first_name, last_name"
			friends = self.session.vk.client.friends.get(count=5000, fields=fields)
		except AttributeError:
			time.sleep(2)
			log.exception("Error retrieving friends...")
			return self.mention(*args, **kwargs)
		users = []
		for i in friends["items"]:
			users.append(u"{0} {1}".format(i["first_name"], i["last_name"]))
		select = selector.selectPeople(users)
		if select.get_response() == widgetUtils.OK and select.users.GetCount() > 0:
			self.tagged_people = []
			tagged_users = select.get_all_users()
			for i in tagged_users:
				self.tagged_people.append(u"[id%s|%s]" % (str(friends["items"][i]["id"]), friends["items"][i]["first_name"]))
			self.message.text.SetValue(self.message.text.GetValue()+ u", ".join(self.tagged_people))

	def translate(self, *args, **kwargs):
		dlg = translator.gui.translateDialog()
		if dlg.get_response() == widgetUtils.OK:
			text_to_translate = self.message.get_text()
			source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			msg = translator.translator.translate(text_to_translate, source, dest)
			self.message.set_text(msg)
			self.message.text_focus()
			output.speak(_(u"Translated"))
		dlg.Destroy()

	def spellcheck(self, event=None):
		text = self.message.get_text()
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.message.set_text(checker.fixed_text)
		checker.clean()

	def show_attach_dialog(self, *args, **kwargs):
		a = attach.attachmentUploader()
		if len(a.attachments) != 0:
			self.attachments = a.attachments

class comment(post):
	def __init__(self, session, title, caption, text):
		super(comment, self).__init__(session, title, caption, text, "comment")
		self.message.set_title(_(u"New comment"))