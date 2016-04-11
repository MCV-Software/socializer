# -*- coding: utf-8 -*-
import widgetUtils
import output
from pubsub import pub
import attach
from wxUI.dialogs import message
from extra import SpellChecker, translator

class post(object):
	def __init__(self, title, caption, text, post_type="post"):
		super(post, self).__init__()
		self.title = title
		self.message = getattr(message, post_type)(title, caption, text)
		self.message.set_title(title)
		widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
		widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
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
		a = attach.attach()
		if len(a.attachments) != 0:
			self.attachments = a.attachments

class comment(post):
	def __init__(self, title, caption, text):
		super(comment, self).__init__(title, caption, text, "comment")
		self.message.set_title(_(u"New comment"))