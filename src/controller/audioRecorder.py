# -*- coding: utf-8 -*-
import time
import os
import tempfile
import sound_lib
import widgetUtils
import sound
import output
from wxUI.dialogs import audioRecorder as gui
from mysc.thread_utils import call_threaded

class audioRecorder(object):
	def __init__(self):
		self.dialog = gui.audioRecorderDialog()
		self.recorded = False
		self.recording = None
		self.duration = 0
		self.playing = None
		widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.on_play)
		widgetUtils.connect_event(self.dialog.pause, widgetUtils.BUTTON_PRESSED, self.on_pause)
		widgetUtils.connect_event(self.dialog.record, widgetUtils.BUTTON_PRESSED, self.on_record)
		widgetUtils.connect_event(self.dialog.discard, widgetUtils.BUTTON_PRESSED, self.on_discard)
		if self.dialog.get_response() == widgetUtils.OK:
			self.postprocess()

	def on_pause(self, *args, **kwargs):
		if self.dialog.get("pause") == _(u"Pause"):
			self.recording.pause()
			self.dialog.set("pause", _(u"&Resume"))
		elif self.dialog.get("pause") == _(u"Resume"):
			self.recording.play()
			self.dialog.set("pause", _(U"&Pause"))

	def on_record(self, *args, **kwargs):
		if self.recording != None:
			self.stop_recording()
			self.dialog.disable_control("pause")
		else:
			self.start_recording()
			self.dialog.enable_control("pause")

	def start_recording(self):
		self.dialog.disable_control("attach_exists")
		self.file = tempfile.mktemp(suffix='.wav')
		self.recording = sound.get_recording(self.file)
		self.duration = time.time()
		self.recording.play()
		self.dialog.set("record", _(u"&Stop"))
		output.speak(_(u"Recording"))

	def stop_recording(self):
		self.recording.stop()
		self.duration = int(time.time()-self.duration)
		self.recording.free()
		output.speak(_(u"Stopped"))
		self.recorded = True
		self.dialog.set("record", _(u"&Record"))
		self.file_attached()

	def file_attached(self):
		self.dialog.set("pause", _(u"&Pause"))
		self.dialog.disable_control("record")
		self.dialog.enable_control("play")
		self.dialog.enable_control("discard")
		self.dialog.disable_control("attach_exists")
		self.dialog.enable_control("attach")
		self.dialog.play.SetFocus()

	def on_discard(self, *args, **kwargs):
		if self.playing:
			self._stop()
		if self.recording != None:
			self.cleanup()
		self.dialog.disable_control("attach")
		self.dialog.disable_control("play")
		self.file = None
		self.dialog.enable_control("record")
		self.dialog.enable_control("attach_exists")
		self.dialog.record.SetFocus()
		self.dialog.disable_control("discard")
		self.recording = None
		output.speak(_(u"Discarded"))

	def on_play(self, *args, **kwargs):
		if not self.playing:
			call_threaded(self._play)
		else:
			self._stop()

	def _play(self):
		output.speak(_(u"Playing..."))
#  try:
		self.playing = sound_lib.stream.FileStream(file=unicode(self.file), flags=sound_lib.stream.BASS_UNICODE)
		self.playing.play()
		self.dialog.set("play", _(u"&Stop"))
		try:
			while self.playing.is_playing:
				pass
			self.dialog.set("play", _(u"&Play"))
			self.playing.free()
			self.playing = None
		except:
			pass

	def _stop(self):
		output.speak(_(u"Stopped"))
		self.playing.stop()
		self.playing.free()
		self.dialog.set("play", _(u"&Play"))
		self.playing = None

	def postprocess(self):
		if self.file.lower().endswith('.wav'):
			output.speak(_(u"Recoding audio..."))
			sound.recode_audio(self.file)
			self.wav_file = self.file
			self.file = '%s.ogg' % self.file[:-4]

	def cleanup(self):
		if self.playing and self.playing.is_playing:
			self.playing.stop()
		if self.recording != None:
			if self.recording.is_playing:
				self.recording.stop()
			try:
				self.recording.free()
			except:
				pass
			os.remove(self.file)
			if hasattr(self, 'wav_file'):
				os.remove(self.wav_file)
