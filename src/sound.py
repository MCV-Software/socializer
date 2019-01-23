# -*- coding: utf-8 -*-
""" Sound utilities for socializer."""
from builtins import range
import sys
import os
import glob
import subprocess
import logging
import paths
import sound_lib
import output
from sound_lib import recording
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded
from sound_lib import output, input

log = logging.getLogger("sound")

def recode_audio(filename, quality=4.5):
	subprocess.call(r'"%s" -q %r "%s"' % (os.path.join(paths.app_path(), 'oggenc2.exe'), quality, filename))

def get_recording(filename):
# try:
	val = recording.WaveRecording(filename=filename)
# except sound_lib.main.BassError:
#  sound_lib.input.Input()
#  val = sound_lib.recording.WaveRecording(filename=filename)
	return val

class soundSystem(object):

	def check_soundpack(self):
		""" Checks if the folder where live the current soundpack exists."""
		self.soundpack_OK = False
		if os.path.exists(os.path.join(paths.sound_path(), self.config["current_soundpack"])):
			self.path = os.path.join(paths.sound_path(), self.config["current_soundpack"])
			self.soundpack_OK = True
		elif os.path.exists(os.path.join(paths.sound_path(), "default")):
			log.error("The soundpack does not exist, using default...")
			self.path = os.path.join(paths.sound_path(), "default")
			self.soundpack_OK = True
		else:
			log.error("The current soundpack could not be found and the default soundpack has been deleted, Socializer will not play sounds.")
			self.soundpack_OK = False

	def __init__(self, soundConfig):
		""" Sound Player."""
		self.config = soundConfig
		# Set the output and input default devices.
		try:
			self.output = output.Output()
			self.input = input.Input()
		except:
			pass
   # Try to use the selected device from the configuration. It can fail if the machine does not has a mic.
		try:
			log.debug("Setting input and output devices...")
			self.output.set_device(self.output.find_device_by_name(self.config["output_device"]))
			self.input.set_device(self.input.find_device_by_name(self.config["input_device"]))
		except:
			log.error("Error in input or output devices, using defaults...")
			self.config["output_device"] = "Default"
			self.config["input_device"] = "Default"

		self.files = []
		self.cleaner = RepeatingTimer(60, self.clear_list)
		self.cleaner.start()
		self.check_soundpack()

	def clear_list(self):
		if len(self.files) == 0: return
		try:
			for i in range(0, len(self.files)):
				if self.files[i].is_playing == False:
					self.files[i].free()
					self.files.pop(i)
		except IndexError:
			pass

	def play(self, sound, argument=False):
		if self.soundpack_OK == False: return
		if self.config["session_mute"] == True: return
		sound_object = sound_lib.stream.FileStream(file="%s/%s" % (self.path, sound))
		sound_object.volume = self.config["volume"]/100
		self.files.append(sound_object)
		sound_object.play()
