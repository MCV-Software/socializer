# -*- coding: utf-8 -*-
""" Attachment upload  methods for different kind of posts in VK. This should become the framework for posting attachment files to the social network."""
import os
import logging
import widgetUtils
from wxUI.dialogs import attach as gui
from wxUI.dialogs import selector
from wxUI.menus import attachMenu
log = logging.getLogger(__file__)

class attachFromLocal(object):
	""" Controller used in some sections of the application, mainly for uploading photos from the local computer to VK.
		This controller will not upload the contents by itself, but will generate the data structures for being sent over the VK API.
		At the current time, only photo uploading is supported."""

	def __init__(self, voice_messages=False):
		""" Constructor.
		@voice_messages bool: If True, will add a button for sending voice messages. Functionality for this button has not been added yet.
		"""
		# Self.attachments will hold a reference to all attachments added to the dialog.
		self.attachments = list()
		# Type is just a reference, as there will be local and online based attachments.
		self.type = "local"
		self.dialog = gui.attachDialog(voice_messages)
		widgetUtils.connect_event(self.dialog.photo, widgetUtils.BUTTON_PRESSED, self.on_image)
		widgetUtils.connect_event(self.dialog.audio, widgetUtils.BUTTON_PRESSED, self.on_audio)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		self.dialog.get_response()
		log.debug("Attachments controller started.")

	def on_image(self, *args, **kwargs):
		m = attachMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.upload_image, menuitem=m.upload)
		self.dialog.PopupMenu(m, self.dialog.photo.GetPosition())

	def on_audio(self, *args, **kwargs):
		m = attachMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.upload_audio, menuitem=m.upload)
		self.dialog.PopupMenu(m, self.dialog.photo.GetPosition())

	def upload_image(self, *args, **kwargs):
		""" allows uploading an image from the computer. In theory
		"""
		image, description  = self.dialog.get_image()
		if image != None:
			# Define data structure for this attachment, as will be required by VK API later.
			imageInfo = {"type": "photo", "file": image, "description": description, "from": "local"}
			log.debug("Image data to upload: %r" % (imageInfo,))
			self.attachments.append(imageInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  a photo.
			info = [_(u"Photo"), description]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def upload_audio(self, *args, **kwargs):
		audio  = self.dialog.get_audio()
		if audio != None:
			# Define data structure for this attachment, as will be required by VK API later.
			audioInfo = {"type": "audio", "file": audio, "from": "local"}
			log.debug("Audio data to upload: %r" % (audioInfo,))
			self.attachments.append(audioInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  a photo.
			info = [_(u"Audio file"), os.path.basename(audio)]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

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

class attachFromOnline(object):
	""" this was the previously working audio attachment uploader. As VK has deprecated their Audio API for third party clients, this class will not work.
	However, I have decided to keep this here so in future it may be modified to attach different kind of online based attachments, such as posted photos, videos, etc.
	"""

	def __init__(self, session):
		""" Default constructor.
		@session vk.session: An VK session, capable of calling methods from the VK API.
		"""
		self.session = session
		# Self.attachments will hold a reference to all attachments added to the dialog.
		self.attachments = list()
		# Define type as online.
		self.type = "online"
		self.dialog = gui.attachDialog()
		widgetUtils.connect_event(self.dialog.audio, widgetUtils.BUTTON_PRESSED, self.add_audio)
#		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		self.dialog.get_response()
		log.debug("Attachments controller started.")

	def add_audio(self, *args, **kwargs):
		""" Allow adding an audio directly from the user's audio library."""
		# Let's reuse the already downloaded audios.
		list_of_audios = self.session.db["me_audio"]["items"]
		audios = []
		for i in list_of_audios:
			audios.append(u"{0}, {1}".format(i["title"], i["artist"]))
		select = selector.selectAttachment(_(u"Select the audio files you want to send"), audios)
		if select.get_response() == widgetUtils.OK and select.attachments.GetCount() > 0:
			attachments = select.get_all_attachments()
			for i in attachments:
				list_of_audios[i]["type"] = "audio"
				self.attachments.append(list_of_audios[i])

	def parse_attachments(self):
		""" Retrieve all attachments and convert them to data structures required by VK API."""
		result = ""
		for i in self.attachments:
			# Define data structures required by VK API.
			preresult = "{0}{1}_{2}".format(i["type"], i["owner_id"], i["id"])
			result = preresult+","
		return result
