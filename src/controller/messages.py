# -*- coding: utf-8 -*-
import widgetUtils
import output
from pubsub import pub
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
#  self.text_processor()
		self.image = None
#		widgetUtils.connect_event(self.message.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)

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
			text_to_translate = self.message.get_text().encode("utf-8")
			source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			msg = translator.translator.translate(text_to_translate, source, dest)
			self.message.set_text(msg)
			self.message.text_focus()
			output.speak(_(u"Translated"))
		else:
			return

# def shorten(self, event=None):
#  urls = utils.find_urls_in_text(self.message.get_text())
#  if len(urls) == 0:
#   output.speak(_(u"There's no URL to be shortened"))
#   self.message.text_focus()
#  elif len(urls) == 1:
#   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.shorten(urls[0])))
#   output.speak(_(u"URL shortened"))
#   self.message.text_focus()
#  elif len(urls) > 1:
#   list_urls = urlList.urlList()
#   list_urls.populate_list(urls)
#   if list_urls.get_response() == widgetUtils.OK:
#    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.shorten(list_urls.get_string())))
#    output.speak(_(u"URL shortened"))
#    self.message.text_focus()

# def unshorten(self, event=None):
#  urls = utils.find_urls_in_text(self.message.get_text())
#  if len(urls) == 0:
#   output.speak(_(u"There's no URL to be expanded"))
#   self.message.text_focus()
#  elif len(urls) == 1:
#   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.unshorten(urls[0])))
#   output.speak(_(u"URL expanded"))
#   self.message.text_focus()
#  elif len(urls) > 1:
#   list_urls = urlList.urlList()
#   list_urls.populate_list(urls)
#   if list_urls.get_response() == widgetUtils.OK:
#    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.unshorten(list_urls.get_string())))
#    output.speak(_(u"URL expanded"))
#    self.message.text_focus()

# def text_processor(self, *args, **kwargs):
#  self.message.set_title(_(u"%s - %s of 140 characters") % (self.title, len(self.message.get_text())))
#  if len(self.message.get_text()) > 1:
#   self.message.enable_button("shortenButton")
#   self.message.enable_button("unshortenButton")
#  else:
#   self.message.disable_button("shortenButton")
#   self.message.disable_button("unshortenButton")
#  if len(self.message.get_text()) > 140:
#   self.session.sound.play("max_length.ogg")

	def spellcheck(self, event=None):
		text = self.message.get_text()
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.message.set_text(checker.fixed_text)

# def attach(self, *args, **kwargs):
#  def completed_callback():
#   url = dlg.uploaderFunction.get_url()
#   pub.unsubscribe(dlg.uploaderDialog.update, "uploading")
#   dlg.uploaderDialog.destroy()
#   if url != 0:
#    self.message.set_text(self.message.get_text()+url+" #audio")
#   else:
#    output.speak(_(u"Unable to upload the audio"))
#   dlg.cleanup()
#  dlg = audioUploader.audioUploader(self.session.settings, completed_callback)

	def upload_image(self, *args, **kwargs):
		if self.message.get("upload_image") == _(u"Discard image"):
			del self.image
			self.image = None
			output.speak(_(u"Discarded"))
			self.message.set("upload_image", _(u"Upload a picture"))
		else:
			self.image = self.message.get_image()
			if self.image != None:
				self.message.set("upload_image", _(u"Discard image"))

class comment(post):
	def __init__(self, title, caption, text):
		super(comment, self).__init__(title, caption, text, "comment")
		self.message.set_title(_(u"New comment"))