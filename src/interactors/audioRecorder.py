# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import widgetUtils
from pubsub import pub
from . import base

class audioRecorderInteractor(base.baseInteractor):
	def install(self, presenter, view, modulename="audiorecorder"):
		super(audioRecorderInteractor, self).install(view=view, presenter=presenter, modulename=modulename)
		widgetUtils.connect_event(view.play, widgetUtils.BUTTON_PRESSED, self.on_play)
		widgetUtils.connect_event(view.record, widgetUtils.BUTTON_PRESSED, self.on_record)
		widgetUtils.connect_event(view.discard, widgetUtils.BUTTON_PRESSED, self.on_discard)

	def start(self):
		result = self.view.get_response()
		if result == widgetUtils.OK:
			self.on_postprocess()

	def on_record(self, *args, **kwargs):
		self.presenter.toggle_recording()

	def on_discard(self, *args, **kwargs):
		self.presenter.discard_recording()

	def on_play(self, *args, **kwargs):
		self.presenter.play()

	def on_postprocess(self):
		self.presenter.postprocess()