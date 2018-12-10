# -*- coding: utf-8 -*-
import widgetUtils
from wxUI.dialogs import configuration as configurationUI

class configuration(object):

	def __init__(self, session):
		self.session = session
		self.dialog = configurationUI.configurationDialog(_(u"Preferences"))
		self.create_config()

	def create_config(self):
		self.dialog.create_general()
		self.dialog.set_value("general", "wall_buffer_count", self.session.settings["buffers"]["count_for_wall_buffers"])
		self.dialog.set_value("general", "video_buffers_count", self.session.settings["buffers"]["count_for_video_buffers"])
		self.dialog.set_value("general", "load_images", self.session.settings["general"]["load_images"])
		self.dialog.realize()
		self.response = self.dialog.get_response()

	def save_configuration(self):
		self.session.settings["buffers"]["count_for_audio_buffers"] = self.dialog.get_value("general", "audio_buffers_count")
		self.session.settings["buffers"]["count_for_video_buffers"] = self.dialog.get_value("general", "video_buffers_count")
		self.session.settings["general"]["load_images"] = self.dialog.get_value("general", "load_images")
		self.session.settings.write()
