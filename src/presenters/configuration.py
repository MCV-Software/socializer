# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pubsub import pub
from . import base

class configurationPresenter(base.basePresenter):

	def __init__(self, session, view, interactor):
		self.session = session
		super(configurationPresenter, self).__init__(view=view, interactor=interactor, modulename="configuration")
		self.create_config()
		self.run()


	def get_notification_label(self, value):
		if value == "native":
			return _("Native")
		else:
			return _("Custom")

	def get_update_channel_label(self, value):
		if value == "stable":
			return _("Stable")
		elif value == "weekly":
			return _("Weekly")
		else:
			return _("Alpha")

	def get_notification_type(self, value):
		if value == _("Native"):
			return "native"
		else:
			return "custom"

	def get_update_channel_type(self, value):
		if value == _("Stable"):
			return "stable"
		elif value == _("Weekly"):
			return "weekly"
		else:
			return "alpha"

	def create_config(self):
		pub.sendMessage("configuration_create_tab", tab="general")
		pub.sendMessage("configuration_set", tab="general", setting="wall_buffer_count", value=self.session.settings["buffers"]["count_for_wall_buffers"])
		pub.sendMessage("configuration_set", tab="general", setting="video_buffers_count", value=self.session.settings["buffers"]["count_for_video_buffers"])
		pub.sendMessage("configuration_set", tab="general", setting="load_images", value=self.session.settings["general"]["load_images"])
		pub.sendMessage("configuration_set", tab="general", setting="update_channel", value=self.get_update_channel_label(self.session.settings["general"]["update_channel"]))
		pub.sendMessage("configuration_create_tab", tab="chat")
		pub.sendMessage("configuration_set", tab="chat", setting="notify_online", value=self.session.settings["chat"]["notify_online"])
		pub.sendMessage("configuration_set", tab="chat", setting="notify_offline", value=self.session.settings["chat"]["notify_offline"])
		pub.sendMessage("configuration_set", tab="chat", setting="open_unread_conversations", value=self.session.settings["chat"]["open_unread_conversations"])
		pub.sendMessage("configuration_set", tab="chat", setting="automove_to_conversations", value=self.session.settings["chat"]["automove_to_conversations"])
		pub.sendMessage("configuration_set", tab="chat", setting="notifications", value=self.get_notification_label(self.session.settings["chat"]["notifications"]))

	def update_setting(self, section, setting, value):
		if section not in self.session.settings:
			raise AttributeError("The configuration section is not present in the spec file.")
		if setting not in self.session.settings[section]:
			raise AttributeError("The setting you specified is not present in the config file.")
		self.session.settings[section][setting] = value

	def save_settings_file(self):
		self.session.settings.write()