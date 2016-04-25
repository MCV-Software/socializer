# -*- coding: utf-8 -*-
import os
import widgetUtils
from wxUI.dialogs import attach as gui

class attach(object):
	def __init__(self):
		self.attachments = list()
		self.dialog = gui.attachDialog()
		widgetUtils.connect_event(self.dialog.photo, widgetUtils.BUTTON_PRESSED, self.upload_image)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
		self.dialog.get_response()

	def upload_image(self, *args, **kwargs):
		image, description  = self.dialog.get_image()
		if image != None:
			self.attachments.append({"type": "photo", "file": image, "description": os.path.basename(image)})
			info = [_(u"Photo"), os.path.basename(image)]
			self.dialog.attachments.insert_item(False, *info)
			self.dialog.remove.Enable(True)

	def remove_attachment(self, *args, **kwargs):
		current_item = self.dialog.attachments.get_selected()
		if current_item == -1: current_item = 0
		self.attachments.pop(current_item)
		self.dialog.attachments.remove_item(current_item)
		self.check_remove_status()

	def check_remove_status(self):
		if len(self.attachments) == 0 and self.dialog.attachments.get_count() == 0:
			self.dialog.remove.Enable(False)
