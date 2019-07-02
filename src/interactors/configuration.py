# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import widgetUtils
from pubsub import pub
from wxUI.commonMessages import restart_program as restart_program_dialog
from . import base

class configurationInteractor(base.baseInteractor):

	def create_tab(self, tab, arglist=dict()):
		getattr(self.view, "create_"+tab)(**arglist)

	def set_setting(self, tab, setting, value):
		self.view.set_value(tab, setting, value)

	def restart(self):
		dlg = restart_program_dialog()
		if dlg == widgetUtils.YES:
			self.presenter.restart_application()

	def set_language(self, language):
		self.view.general.language.SetSelection(language)

	def install(self, *args, **kwargs):
		super(configurationInteractor, self).install(*args, **kwargs)
		pub.subscribe(self.create_tab, self.modulename+"_create_tab")
		pub.subscribe(self.set_setting, self.modulename+"_set")
		pub.subscribe(self.restart, self.modulename+"_restart_program")
		pub.subscribe(self.set_language, self.modulename+"_set_language")

	def uninstall(self):
		super(configurationInteractor, self).uninstall()
		pub.unsubscribe(self.create_tab, self.modulename+"_create_tab")
		pub.unsubscribe(self.set_setting, self.modulename+"_set")
		pub.unsubscribe(self.restart, self.modulename+"_restart_program")
		pub.unsubscribe(self.set_language, self.modulename+"_set_language")

	def start(self):
		self.view.realize()
		result = self.view.get_response()
		if result == widgetUtils.OK:
			self.on_save_settings()

	def on_save_settings(self, *args, **kwargs):
		self.presenter.update_setting(section="buffers", setting="count_for_wall_buffers", value=self.view.get_value("general", "wall_buffer_count"))
		self.presenter.update_setting(section="buffers", setting="count_for_video_buffers", value=self.view.get_value("general", "video_buffers_count"))
		self.presenter.update_setting(section="general", setting="load_images", value=self.view.get_value("general", "load_images"))
		update_channel = self.presenter.get_update_channel_type(self.view.get_value("general", "update_channel"))
		if update_channel != self.presenter.session.settings["general"]["update_channel"]:
			if update_channel == "stable":
				self.presenter.update_setting(section="general", setting="update_channel", value=update_channel)
			elif update_channel == "weekly":
				dialog = self.view.weekly_channel()
				if dialog == widgetUtils.YES:
					self.presenter.update_setting(section="general", setting="update_channel", value=update_channel)
			elif update_channel == "alpha":
				dialog = self.view.alpha_channel()
				if dialog == widgetUtils.YES:
					self.presenter.update_setting(section="general", setting="update_channel", value=update_channel)
		self.presenter.update_setting(section="chat", setting="notify_online", value=self.view.get_value("chat", "notify_online"))
		self.presenter.update_setting(section="chat", setting="notify_offline", value=self.view.get_value("chat", "notify_offline"))
		self.presenter.update_setting(section="chat", setting="notifications", value=self.presenter.get_notification_type(self.view.get_value("chat", "notifications")))
		self.presenter.update_setting(section="load_at_startup", setting="audio_albums", value=self.view.get_value("startup", "audio_albums"))
		self.presenter.update_setting(section="load_at_startup", setting="video_albums", value=self.view.get_value("startup", "video_albums"))
		self.presenter.update_setting(section="load_at_startup", setting="communities", value=self.view.get_value("startup", "communities"))
		self.presenter.update_app_setting(section="app-settings", setting="language", value=self.presenter.codes[self.view.general.language.GetSelection()])
		self.presenter.update_app_setting(section="sound", setting="input_device", value=self.view.get_value("sound", "input"))
		self.presenter.update_app_setting(section="sound", setting="output_device", value=self.view.get_value("sound", "output"))
		self.presenter.update_app_setting(section="app-settings", setting="use_proxy", value=self.view.get_value("general", "use_proxy"))
		self.presenter.save_app_settings_file()
		self.presenter.save_settings_file()
