# -*- coding: utf-8 -*-
""" High level Spell checker module by using the SymSpellPy library. """
import os
import glob
import shutil
import logging
import paths
from symspellpy.symspellpy import SymSpell, Verbosity
from codecs import open as open_

log = logging.getLogger("SpellChecker.checker")

loaded_dicts = dict()
ready = False

def load_dicts():
	global loaded_dicts, ready
	log.debug("Start dictionary loading for spelling checker module...")
	if len(loaded_dicts) > 0:
		loaded_dicts = dict()
	path = os.path.join(paths.config_path(), "dicts")
	if os.path.isdir(path):
		log.debug("Loading language dictionaries from path %s" % (path,))
		files = glob.glob(os.path.join(path, "*.txt"))
		log.debug("%r files found." % (len(files)))
		for i in files:
			key = os.path.splitext(os.path.basename(i))[0]
			dictionary = SymSpell()
			dictionary.load_dictionary(i, 0, 1, encoding="utf-8")
			loaded_dicts[key] = dictionary
			log.debug("Added dictionary for language %s " % (key,))
	ready = True
	log.debug("All dicts were loaded.")

def prepare_dicts(language):
	""" Copy the main dictionary file to the user's config directory so it can be modified and read without needing to require privileged sessions.
	@ language: two letter language code.
	"""
	log.debug("preparing dictionary data...")
	path = os.path.join(paths.config_path(), "dicts")
	if os.path.exists(path) == False:
		log.debug("Creating dicts folder in config directory...")
		os.mkdir(path)
	original_file = os.path.join(paths.app_path(), "dictionaries", language+".txt")
	if os.path.exists(original_file) and os.path.exists(os.path.join(paths.config_path(), "dicts", language+".txt")) == False:
		log.debug("Dictionary for language %s is not present in user config. Coppying... " % (language,))
		dst_file = shutil.copy(original_file, os.path.join(paths.config_path(), "dicts"))

class SpellChecker(object):

	def __init__(self, wordlist=None, *args, **kwargs):
		self.kwargs = kwargs
		self.dictionary = None
		self.ignored_words = []
		self.word_index = 0

	def set_language(self, lang):
		global loaded_dicts
		if loaded_dicts.get(lang) != None:
			self.dictionary = loaded_dicts[lang]
		else:
			raise ValueError("Dictionary not found for the specified language")

	def set_text(self, text):
		self.transformed_words = text.split()
		self.word_index = 0

	def check_words(self):
		for word in range(0, len(self.transformed_words)):
			if self.transformed_words[word] in self.ignored_words:
				continue
			suggestions = self.dictionary.lookup(self.transformed_words[word], Verbosity.CLOSEST, 2, transfer_casing=True)
			valid_word = True
			if len(suggestions) == 0:
				continue
			for s in suggestions:
				print(s.term)
				print(s.distance)
				if s.distance == 0:
					valid_word = False
			if valid_word == False:
				continue
			if word <= 10:
				if len(self.transformed_words) <= 10:
					context = " ".join(self.transformed_words)
				else:
					context = " ".join(self.transformed_words[0:10])
			elif word >= len(self.transformed_words)-9:
				context = " ".join(self.transformed_words[-10])
			else:
				context = " ".join(self.transformed_words[word-5:word+5])
			self.word_index = word
#			print(self.word)
#			print(suggestions[0].distance)
			yield (suggestions, context, word)

	def replace(self, suggestion):
		if len(self.transformed_words) < self.word_index:
			raise ValueError("Word index is not present in the current text")
		self.transformed_words[self.word_index] = suggestion

	def replace_all(self, word):
		existing_word = self.word
		for i in range(0, len(self.transformed_words)):
			if self.transformed_words[i] == existing_word:
				self.transformed_words[i] = word

	def ignore_word(self, word):
		self.ignored_words.append(word)

	@property
	def text(self):
		return " ".join(self.transformed_words)

	@property
	def word(self):
		if len(self.transformed_words) == 0 or self.word_index >= len(self.transformed_words):
			return None
		return self.transformed_words[self.word_index]