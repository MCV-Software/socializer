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
		self.is_working = False

	def play(self, url):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
		# Make sure that  there are no other sounds trying to be played.
		if self.is_working == False:
			self.is_working = True
			self.stream = URLStream(url=url)
			self.stream.volume = self.vol/100.0
			self.stream.play()
			self.is_working = False

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
		if vol <= 100 and vol >= 0:
			self.vol = vol
		if self.stream != None:
			self.stream.volume = self.vol/100.0

