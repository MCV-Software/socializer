# -*- coding: utf-8 -*-
""" Attachment controller for different kind of posts in VK.
this controller will take care of preparing data structures to be uploaded later, when the user decides to start the upload process by sending the post.
"""
from __future__ import unicode_literals
import os
import logging
import widgetUtils
from . import audioRecorder
from mutagen.id3 import ID3
from sessionmanager.utils import seconds_to_string
from wxUI.dialogs import attach as gui
from wxUI.dialogs import selector
from wxUI.menus import attachMenu

log = logging.getLogger(__file__)

class attach(object):
	""" Controller used in some sections of the application, it can do the following:

	* Handle all user input related to adding local or online files (online files are those already uploaded in vk).
	* Prepare local files to be uploaded once a post will be sent (no uploading work is done here, but structured dicts will be generated).
	* Parse online files and allow addition of them as attachment, so this controller will add both local and online files in the same dialog.
"""

	def __init__(self, session, voice_messages=False):
		""" Constructor.
	@ session sessionmanager.session object: an object capable of calling all VK methods and accessing the session database.
		@voice_messages bool: If True, will add a button for sending voice messages. Functionality for this button has not been added yet.
		"""
		self.session = session
		# Self.attachments will hold a reference to all attachments added to the dialog.
		self.attachments = list()
		self.dialog = gui.attachDialog(voice_messages)
		widgetUtils.connect_event(self.dialog.photo, widgetUtils.BUTTON_PRESSED, self.on_image)
		widgetUtils.connect_event(self.dialog.audio, widgetUtils.BUTTON_PRESSED, self.on_audio)
		if voice_messages:
			widgetUtils.connect_event(self.dialog.voice_message, widgetUtils.BUTTON_PRESSED, self.upload_voice_message)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		log.debug("Attachments controller started.")
		self.dialog.get_response()

	def on_image(self, *args, **kwargs):
		""" display menu for adding image attachments. """
		m = attachMenu()
		# disable add from VK as it is not supported in images, yet.
		m.add.Enable(False)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.upload_image, menuitem=m.upload)
		self.dialog.PopupMenu(m, self.dialog.photo.GetPosition())

	def on_audio(self, *args, **kwargs):
		""" display menu to add audio attachments."""
		m = attachMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.upload_audio, menuitem=m.upload)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.add_audio, menuitem=m.add)
		self.dialog.PopupMenu(m, self.dialog.audio.GetPosition())

	def upload_image(self, *args, **kwargs):
		""" allows uploading an image from the computer.
		"""
		image, description  = self.dialog.get_image()
		if image != None:
			# Define data structure for this attachment, as will be required by VK API later.
			imageInfo = {"type": "photo", "file": image, "description": description, "from": "local"}
			self.attachments.append(imageInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  a photo.
			info = [_("Photo"), description]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def upload_audio(self, *args, **kwargs):
		""" Allows uploading an audio file from the computer. Only mp3 files are supported. """
		audio  = self.dialog.get_audio()
		if audio != None:
			# Define data structure for this attachment, as will be required by VK API later.
			# Let's extract the ID3 tags to show them in the list and send them to VK, too.
			audio_tags = ID3(audio)
			if "TIT2" in audio_tags:
				title = audio_tags["TIT2"].text[0]
			else:
				title = _("Untitled")
			if "TPE1" in audio_tags:
				artist = audio_tags["TPE1"].text[0]
			else:
				artist = _("Unknown artist")
			audioInfo = {"type": "audio", "file": audio, "from": "local", "title": title, "artist": artist}
			self.attachments.append(audioInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
			info = [_("Audio file"), "{title} - {artist}".format(title=title, artist=artist)]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def upload_voice_message(self, *args, **kwargs):
		a = audioRecorder.audioRecorder()
		if a.file != None and a.duration != 0:
			audioInfo = {"type": "voice_message", "file": a.file, "from": "local"}
			self.attachments.append(audioInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
			info = [_("Voice message"), seconds_to_string(a.duration,)]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def add_audio(self, *args, **kwargs):
		""" Allow adding an audio directly from the user's audio library."""
		# Let's reuse the already downloaded audios.
		list_of_audios = self.session.db["me_audio"]["items"]
		audios = []
		for i in list_of_audios:
			audios.append("{0}, {1}".format(i["title"], i["artist"]))
		select = selector.selectAttachment(_("Select the audio files you want to send"), audios)
		if select.get_response() == widgetUtils.OK and select.attachments.GetCount() > 0:
			attachments = select.get_all_attachments()
			for i in attachments:
				info = dict(type="audio", id=list_of_audios[i]["id"], owner_id=list_of_audios[i]["owner_id"])
				info["from"] = "online"
				self.attachments.append(info)
				# Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
				info2 = [_("Audio file"), "{0} - {1}".format(list_of_audios[i]["title"], list_of_audios[i]["artist"])]
				self.dialog.attachments.insert_item(False, *info2)
		self.check_remove_status()

	def remove_attachment(self, *args, **kwargs):
		""" Remove the currently focused item from the attachments list."""
		current_item = self.dialog.attachments.get_selected()
		log.debug("Removing item %d" % (current_item,))
		if current_item == -1: current_item = 0
		self.attachments.pop(current_item)
		self.dialog.attachments.remove_item(current_item)
		self.check_remove_status()
		log.debug("Removed")

	def check_remove_status(self):
		""" Checks whether the remove button should remain enabled."""
		if len(self.attachments) == 0 and self.dialog.attachments.get_count() == 0:
			self.dialog.remove.Enable(False)
