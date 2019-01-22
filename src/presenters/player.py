# -*- coding: utf-8 -*-
import sys
import random
import output
import sound_lib
import logging
import config
from sound_lib.config import BassConfig
from sound_lib.stream import URLStream
from sound_lib.main import BassError
from mysc.repeating_timer import RepeatingTimer
from pubsub import pub

player = None
log = logging.getLogger("player")

def setup():
	global player
	if player == None:
		player = audioPlayer()

class audioPlayer(object):

	def __init__(self):
		self.is_playing = False
		self.stream = None
		self.vol = config.app["sound"]["volume"]
		self.is_working = False
		self.queue = []
		self.playing_track = 0
		self.stopped = True
		# Modify some default settings present in Bass so it will increase timeout connection, thus causing less "connection timed out" errors when playing.
		bassconfig = BassConfig()
		# Set timeout connection to 30 seconds.
		bassconfig["net_timeout"] = 30000
		# Adds proxy settings
		if config.app["app-settings"]["use_proxy"] == True:
			bassconfig["net_proxy"] = b"socializer:socializer@socializer.su:3128"

	def play(self, url, set_info=True, fresh=False):
		if self.stream != None and self.stream.is_playing == True:
			try:
				self.stream.stop()
			except BassError:
				log.exception("error when stopping the file")
				self.stream = None
			self.stopped = True
			if fresh == True and hasattr(self, "worker") and self.worker != None:
				self.worker.cancel()
				self.worker = None
				self.queue = []
		# Make sure that  there are no other sounds trying to be played.
		if self.is_working == False:
			self.is_working = True
			# Let's encode the URL as bytes if on Python 3
			if sys.version[0] == "3":
				url_ = bytes(url["url"], "utf-8")
			else:
				url_ = url["url"]
			try:
				self.stream = URLStream(url=url_)
			except IndexError:
				log.error("Unable to play URL")
				log.error(url_)
				return
			# Translators: {0} will be replaced with a song's title and {1} with the artist.
			if set_info:
				msg = _("Playing {0} by {1}").format(url["title"], url["artist"])
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
				try:
					self.stream.play()
					self.stopped = False
				except BassError:
					pass

	@property
	def volume(self):
		return self.vol

	@volume.setter
	def volume(self, vol):
		if vol <= 100 and vol >= 0:
			self.vol = vol
		if self.stream != None:
			self.stream.volume = self.vol/100.0

	def play_all(self, list_of_urls, shuffle=False):
		self.playing_track = 0
		self.stop()
		# Skip all country restricted tracks as they are not playable here.
		self.queue = [i for i in list_of_urls if i["url"] != ""]
		if shuffle:
			random.shuffle(self.queue)
		self.play(self.queue[self.playing_track])
		self.worker = RepeatingTimer(5, self.player_function)
		self.worker.start()

	def player_function(self):
		if self.stream != None and self.stream.is_playing == False and self.stopped == False and len(self.stream) == self.stream.position:
			if len(self.queue) == 0 or self.playing_track >= len(self.queue):
				self.worker.cancel()
				return
			if self.playing_track < len(self.queue):
				self.playing_track += 1
			self.play(self.queue[self.playing_track])

	def play_next(self):
		if len(self.queue) == 0:
			return
		if self.playing_track < len(self.queue):
			self.playing_track += 1
		else:
			self.playing_track = 0
		self.play(self.queue[self.playing_track])

	def play_previous(self):
		if len(self.queue) == 0:
			return
		if self.playing_track <= 0:
			self.playing_track = len(self.queue)-1
		else:
			self.playing_track -= 1
		self.play(self.queue[self.playing_track])

	def check_is_playing(self):
		if self.stream == None:
			return False
		if self.stream != None and self.stream.is_playing == False:
			return False
		else:
			return True

