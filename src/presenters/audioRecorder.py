# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import os
import tempfile
import sound_lib
import sound
import output
from mysc.thread_utils import call_threaded
from . import base

class audioRecorderPresenter(base.basePresenter):
    def __init__(self, view, interactor):
        super(audioRecorderPresenter, self).__init__(view=view, interactor=interactor, modulename="audiorecorder")
        self.recorded = False
        self.recording = None
        self.duration = 0
        self.playing = None
        self.file = None
        self.run()

    def toggle_recording(self, *args, **kwargs):
        if self.recording != None:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.file = tempfile.mktemp(suffix='.wav')
        self.recording = sound.get_recording(self.file)
        self.duration = time.time()
        self.recording.play()
        self.send_message("set_label", control="record", label=_("&Stop"))
        output.speak(_("Recording"))
        self.send_message("disable_control", control="ok")

    def stop_recording(self):
        self.recording.stop()
        self.duration = int(time.time()-self.duration)
        self.recording.free()
        output.speak(_("Stopped"))
        self.recorded = True
        self.send_message("set_label", control="record", label=_("&Record"))
        self.send_message("disable_control", control="record")
        self.send_message("enable_control", control="play")
        self.send_message("enable_control", control="discard")
        self.send_message("enable_control", control="ok")
        self.send_message("focus_control", control="play")

    def discard_recording(self, *args, **kwargs):
        if self.playing:
            self._stop()
        if self.recording != None:
            self.cleanup()
        self.send_message("disable_control", control="play")
        self.send_message("disable_control", control="ok")
        self.file = None
        self.send_message("enable_control", control="record")
        self.send_message("focus_control", control="record")
        self.send_message("disable_control", control="discard")
        self.recording = None
        output.speak(_("Discarded"))

    def play(self, *args, **kwargs):
        if not self.playing:
            call_threaded(self._play)
        else:
            self._stop()

    def _play(self):
        output.speak(_("Playing..."))
#  try:
        self.playing = sound_lib.stream.FileStream(file=str(self.file), flags=sound_lib.stream.BASS_UNICODE)
        self.playing.play()
        self.send_message("set_label", control="play", label=_("&Stop"))
        try:
            while self.playing.is_playing:
                pass
            self.send_message("set_label", control="play", label=_("&Play"))
            self.playing.free()
            self.playing = None
        except:
            pass

    def _stop(self):
        output.speak(_("Stopped"))
        self.playing.stop()
        self.playing.free()
        self.send_message("set_label", control="play", label=_("&Play"))
        self.playing = None

    def postprocess(self):
        if self.file.lower().endswith('.wav'):
            output.speak(_("Recoding audio..."))
            sound.recode_audio(self.file)
            self.wav_file = self.file
            self.file = '%s.ogg' % self.file[:-4]
            self.cleanup()

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
            if hasattr(self, 'wav_file'):
                os.remove(self.wav_file)
