# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import logging
import widgetUtils
import output
import config
import languageHandler
from platform_utils import paths
from . import checker
from . import wx_ui

log = logging.getLogger("extra.SpellChecker.spellChecker")

class spellChecker(object):
	def __init__(self, text):
		super(spellChecker, self).__init__()
		self.active = True
		self.checker = checker.SpellChecker()
		log.debug("Using language: %s" % (languageHandler.getLanguage(),))
		try:
			self.checker.set_language(languageHandler.curLang[:2])
		except ValueError:
			log.exception("Dictionary for language %s not found." % (languageHandler.curLang,))
			wx_ui.dict_not_found_error()
			self.active = False
		self.checker.set_text(text)
		self.generator = self.checker.check_words()
		if self.active == True:
			log.debug("Creating dialog...")
			self.dialog = wx_ui.spellCheckerDialog()
			widgetUtils.connect_event(self.dialog.ignore, widgetUtils.BUTTON_PRESSED, self.ignore)
			widgetUtils.connect_event(self.dialog.ignoreAll, widgetUtils.BUTTON_PRESSED, self.ignoreAll)
			widgetUtils.connect_event(self.dialog.replace, widgetUtils.BUTTON_PRESSED, self.replace)
			widgetUtils.connect_event(self.dialog.replaceAll, widgetUtils.BUTTON_PRESSED, self.replaceAll)
			self.check()
			self.dialog.get_response()
			self.fixed_text = self.checker.text

	def check(self):
		try:
			suggestions, context, self.wordIndex = next(self.generator)
			textToSay = _("Misspelled word: %s") % (self.checker.word,)
			context = context
			self.dialog.set_title(textToSay)
			output.speak(textToSay)
			self.dialog.set_word_and_suggestions(word=self.checker.word, context=context, suggestions=[suggestion.term for suggestion in suggestions])
		except StopIteration:
			log.debug("Process finished.")
			wx_ui.finished()
			self.dialog.Destroy()

	def ignore(self, ev):
		self.check()

	def ignoreAll(self, ev):
		self.checker.ignore_word(word=self.checker.word)
		self.check()

	def replace(self, ev):
		self.checker.replace(self.dialog.get_selected_suggestion())
		self.check()

	def replaceAll(self, ev):
		self.checker.replace_all(self.dialog.get_selected_suggestion())
		self.check()

	def clean(self):
		if hasattr(self, "dialog"):
			self.dialog.Destroy()