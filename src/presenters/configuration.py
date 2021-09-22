# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sound_lib.input, sound_lib.output
import config
import languageHandler
from mysc import restart
from . import base

class configurationPresenter(base.basePresenter):

    def __init__(self, session, view, interactor):
        self.session = session
        super(configurationPresenter, self).__init__(view=view, interactor=interactor, modulename="configuration")
        # Control requirement for a restart of the application.
        self.needs_restart = False
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
        self.langs = languageHandler.getAvailableLanguages()
        langs = [i[1] for i in self.langs]
        self.codes = [i[0] for i in self.langs]
        id = self.codes.index(config.app["app-settings"]["language"])
        self.send_message("create_tab", tab="general", arglist=dict(languages=langs))
        self.send_message("set_language", language=id)
        self.send_message("set", tab="general", setting="load_images", value=self.session.settings["general"]["load_images"])
        self.send_message("set", tab="general", setting="use_proxy", value=config.app["app-settings"]["use_proxy"])
        self.send_message("set", tab="general", setting="debug_logging", value=config.app["app-settings"]["debug_logging"])
        self.send_message("set", tab="general", setting="update_channel", value=self.get_update_channel_label(self.session.settings["general"]["update_channel"]))
        self.send_message("create_tab", tab="buffers")
        self.send_message("set", tab="buffers", setting="wall_buffer_count", value=self.session.settings["buffers"]["count_for_wall_buffers"])
        self.send_message("set", tab="buffers", setting="video_buffers_count", value=self.session.settings["buffers"]["count_for_video_buffers"])
        self.send_message("set", tab="buffers", setting="chat_buffers_count", value=self.session.settings["buffers"]["count_for_chat_buffers"])
        self.send_message("create_tab", tab="chat")
        self.send_message("set", tab="chat", setting="notify_online", value=self.session.settings["chat"]["notify_online"])
        self.send_message("set", tab="chat", setting="notify_offline", value=self.session.settings["chat"]["notify_offline"])
        self.send_message("set", tab="chat", setting="notifications", value=self.get_notification_label(self.session.settings["chat"]["notifications"]))
        self.send_message("create_tab", tab="startup_options")
        self.send_message("set", tab="startup", setting="audio_albums", value=self.session.settings["load_at_startup"]["audio_albums"])
        self.send_message("set", tab="startup", setting="video_albums", value=self.session.settings["load_at_startup"]["video_albums"])
        self.send_message("set", tab="startup", setting="communities", value=self.session.settings["load_at_startup"]["communities"])
        self.input_devices = sound_lib.input.Input.get_device_names()
        self.output_devices = sound_lib.output.Output.get_device_names()
        self.send_message("create_tab", tab="sound", arglist=dict(input_devices=self.input_devices, output_devices=self.output_devices, soundpacks=[]))
        self.send_message("set", tab="sound", setting="input", value=config.app["sound"]["input_device"])
        self.send_message("set", tab="sound", setting="output", value=config.app["sound"]["output_device"])

    def update_setting(self, section, setting, value):
        if section not in self.session.settings:
            raise AttributeError("The configuration section is not present in the spec file.")
        if setting not in self.session.settings[section]:
            raise AttributeError("The setting you specified is not present in the config file.")
        self.session.settings[section][setting] = value

    def save_settings_file(self):
        self.session.settings.write()

    def update_app_setting(self, section, setting, value):
        if section not in config.app:
            raise AttributeError("The configuration section is not present in the spec file.")
        if setting not in config.app[section]:
            raise AttributeError("The setting you specified is not present in the config file.")
        # check if certain settings have been changed so we'd restart the client.
        # List of app settings that require a restart after being changed.
        settings_needing_restart = ["language", "use_proxy", "input_device", "output_device", "debug_logging"]
        if value != config.app[section][setting] and setting in settings_needing_restart:
            self.needs_restart = True
        config.app[section][setting] = value

    def save_app_settings_file(self):
        config.app.write()
        if self.needs_restart:
            self.send_message("restart_program")

    def restart_application(self):
        restart.restart_program()
