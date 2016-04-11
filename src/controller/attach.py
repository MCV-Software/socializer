# -*- coding: utf-8 -*-
import os
import widgetUtils
from wxUI.dialogs import attach as gui

class attach(object):
	def __init__(self):
		self.attachments = list()
		self.dialog = gui.attachDialog()
		widgetUtils.connect_event(self.dialog.photo, widgetUtils.BUTTON_PRESSED, self.upload_image)
		self.dialog.get_response()

	def upload_image(self, *args, **kwargs):
		image, description  = self.dialog.get_image()
		if image != None:
			self.attachments.append({"type": "photo", "file": image, "description": os.path.basename(image)})
			info = [_(u"Photo"), os.path.basename(image)]
			self.dialog.attachments.insert_item(False, *info)