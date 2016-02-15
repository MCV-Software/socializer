# -*- coding: utf-8 -*-
import sound_lib
from sound_lib.output import Output
from sound_lib.stream import URLStream

player = None

def setup():
	global player
	if player == None:
		player = audioPlayer()

class audioPlayer(object):

	def __init__(self):
		Output()
		self.is_playing = False
		self.stream = None
		self.vol = 100

	def play(self, url):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
		self.stream = URLStream(url=url)
		self.stream.volume = self.vol/100.0
		self.stream.play()

	def stop(self):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()

	def pause(self):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.pause()

	@property
	def volume(self):
		if self.stream != None:
			return self.vol

	@volume.setter
	def volume(self, vol):
		self.vol = vol
		if self.stream != None:
			self.stream.volume = vol/100.0

