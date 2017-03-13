# -*- coding: utf-8 -*-
""" Attachment upload  methods for different kind of posts in VK."""
import os
import widgetUtils
import logging
from wxUI.dialogs import attach as gui
from wxUI.dialogs import selector
log = logging.getLogger("controller.attach")

class attachmentUploader(object):
	def __init__(self, voice_messages=False):
		self.attachments = list()
		self.type = "local"
		self.dialog = gui.attachDialog(voice_messages)
		widgetUtils.connect_event(self.dialog.photo, widgetUtils.BUTTON_PRESSED, self.upload_image)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		self.dialog.get_response()
		log.debug("Attachments controller started.")

	def upload_image(self, *args, **kwargs):
		image, description  = self.dialog.get_image()
		if image != None:
			imageInfo = {"type": "photo", "file": image, "description": os.path.basename(image)}
			log.debug("Image data to upload: %r" % (imageInfo,))
			self.attachments.append(imageInfo)
			# Translators: This is the text displayed in the attachments dialog, when the user adds  a photo.
			info = [_(u"Photo"), os.path.basename(image)]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def remove_attachment(self, *args, **kwargs):
		current_item = self.dialog.attachments.get_selected()
		log.debug("Removing item %d" % (current_item,))
		if current_item == -1: current_item = 0
		self.attachments.pop(current_item)
		self.dialog.attachments.remove_item(current_item)
		self.check_remove_status()
		log.debug("Removed")

	def check_remove_status(self):
		if len(self.attachments) == 0 and self.dialog.attachments.get_count() == 0:
			self.dialog.remove.Enable(False)

class attach(object):

	def __init__(self, session):
		self.session = session
		self.attachments = list()
		self.type = "online"
		self.dialog = gui.attachDialog()
		widgetUtils.connect_event(self.dialog.audio, widgetUtils.BUTTON_PRESSED, self.add_audio)
#		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		self.dialog.get_response()
		log.debug("Attachments controller started.")

	def add_audio(self, *args, **kwargs):
		list_of_audios = self.session.vk.client.audio.get(count=1000)
		list_of_audios = list_of_audios["items"]
		audios = []
		for i in list_of_audios:
			audios.append(u"{0}, {1}".format(i["title"], i["artist"]))
		select = selector.selectAttachment(_(u"Select the audio files you want to send"), audios)
		if select.get_response() == widgetUtils.OK and select.attachments.GetCount() > 0:
			attachments = select.get_all_attachments()
			for i in attachments:
				print list_of_audios[i].keys()
				list_of_audios[i]["type"] = "audio"
				self.attachments.append(list_of_audios[i])

	def parse_attachments(self):
		result = ""
		for i in self.attachments:
			preresult = "{0}{1}_{2}".format(i["type"], i["owner_id"], i["id"])
			result = preresult+","
		return result