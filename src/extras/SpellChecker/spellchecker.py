# -*- coding: utf-8 -*-
import logging
import wx_ui
import widgetUtils
import output
import config
import languageHandler
from enchant.checker import SpellChecker
from enchant.errors import DictNotFoundError
from enchant import tokenize

log = logging.getLogger("extra.SpellChecker.spellChecker")

class spellChecker(object):
	def __init__(self, text, dictionary):
		super(spellChecker, self).__init__()
		log.debug("Creating the SpellChecker object. Dictionary: %s" % (dictionary,))
		self.active = True
		try:
			if config.app["app-settings"]["language"] == "system":
				log.debug("Using the system language")
				self.checker = SpellChecker(languageHandler.curLang, filters=[tokenize.EmailFilter, tokenize.URLFilter])
			else:
				log.debug("Using language: %s" % (languageHandler.getLanguage(),))
				self.checker = SpellChecker(languageHandler.curLang, filters=[tokenize.EmailFilter, tokenize.URLFilter])
			self.checker.set_text(text)
		except DictNotFoundError:
			print "no dict"
			log.exception("Dictionary for language %s not found." % (dictionary,))
			wx_ui.dict_not_found_error()
			self.active = False
		if self.active == True:
			log.debug("Creating dialog...")
			self.dialog = wx_ui.spellCheckerDialog()
			widgetUtils.connect_event(self.dialog.ignore, widgetUtils.BUTTON_PRESSED, self.ignore)
			widgetUtils.connect_event(self.dialog.ignoreAll, widgetUtils.BUTTON_PRESSED, self.ignoreAll)
			widgetUtils.connect_event(self.dialog.replace, widgetUtils.BUTTON_PRESSED, self.replace)
			widgetUtils.connect_event(self.dialog.replaceAll, widgetUtils.BUTTON_PRESSED, self.replaceAll)
			self.check()
			self.dialog.get_response()
			self.fixed_text = self.checker.get_text()

	def check(self):
		try:
			self.checker.next()
			textToSay = _(u"Misspelled word: %s") % (self.checker.word,)
			context = u"... %s %s %s" % (self.checker.leading_context(10), self.checker.word, self.checker.trailing_context(10))
			self.dialog.set_title(textToSay)
			output.speak(textToSay)
			self.dialog.set_word_and_suggestions(word=self.checker.word, context=context, suggestions=self.checker.suggest())
		except StopIteration:
			log.debug("Process finished.")
			wx_ui.finished()
			self.dialog.Destroy()

	def ignore(self, ev):
		self.check()

	def ignoreAll(self, ev):
		self.checker.ignore_always(word=self.checker.word)
		self.check()

	def replace(self, ev):
		self.checker.replace(self.dialog.get_selected_suggestion())
		self.check()

	def replaceAll(self, ev):
		self.checker.replace_always(self.dialog.get_selected_suggestion())
		self.check()

	def clean(self):
		if hasattr(self, "dialog"):
			self.dialog.Destroy()