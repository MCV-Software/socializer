# -*- coding: utf-8 -*-
import output
import sound_lib
from sound_lib.stream import URLStream
from mysc.repeating_timer import RepeatingTimer
from pubsub import pub

player = None

def setup():
	global player
	if player == None:
		player = audioPlayer()

class audioPlayer(object):

	def __init__(self):
		self.is_playing = False
		self.stream = None
		self.vol = 100
		self.is_working = False
		self.queue = []
		self.stopped = True

	def play(self, url):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
			self.stopped = True
			if hasattr(self, "worker") and self.worker != None:
				self.worker.cancel()
				self.worker = None
				self.queue = []
		# Make sure that  there are no other sounds trying to be played.
		if self.is_working == False:
			self.is_working = True
			self.stream = URLStream(url=url["url"])
			# Translators: {0} will be replaced with a song's title and {1} with the artist.
			msg = _(u"Playing {0} by {1}").format(url["title"], url["artist"])
			pub.sendMessage("update-status-bar", status=msg)
			self.stream.volume = self.vol/100.0
			self.stream.play()
			self.stopped = False
			self.is_working = False

	def stop(self):
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
			self.stopped = True
		if hasattr(self, "worker") and self.worker != None:
			self.worker.cancel()
			self.worker = None
			self.queue = []

	def pause(self):
		if self.stream != None:
			if self.stream.is_playing == True:
				self.stream.pause()
				self.stopped = True
			else:
				self.stream.play()
				self.stopped = False

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

	def play_all(self, list_of_urls):
		self.stop()
		self.queue = list_of_urls
		self.play(self.queue[0])
		self.queue.remove(self.queue[0])
		self.worker = RepeatingTimer(5, self.player_function)
		self.worker.start()

	def player_function(self):
		if self.stream != None and self.stream.is_playing == False and self.stopped == False:
			if len(self.queue) == 0:
				self.worker.cancel()
				return
			self.play(self.queue[0])
			self.queue.remove(self.queue[0])
