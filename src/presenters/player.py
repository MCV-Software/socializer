# -*- coding: utf-8 -*-
""" Audio player module for socializer.
As this player does not have (still) an associated GUI, I have decided to place here the code for the interactor, which connects a bunch of pubsub events, and the presenter itself.
"""
import sys
import random
import logging
import sound_lib
import output
import config
from sound_lib.config import BassConfig
from sound_lib.stream import URLStream
from sound_lib.main import BassError
from pubsub import pub
from mysc.repeating_timer import RepeatingTimer

player = None
log = logging.getLogger("player")

# This function will be deprecated when the player works with pubsub events, as will no longer be needed to instantiate and import the player directly.
def setup():
	global player
	if player == None:
		player = audioPlayer()

class audioPlayer(object):
	""" A media player which will play all passed URLS."""

	def __init__(self):
		# control variable for checking if another file has been sent to the player before,
		# thus avoiding double file playback and other oddities happening in sound_lib from time to time.
		self.is_playing = False
		# This will be the URLStream handler
		self.stream = None
		self.vol = config.app["sound"]["volume"]
		# this variable is set to true when the URLPlayer is decoding something, thus it will block other calls to the play method.
		self.is_working = False
		# Playback queue.
		self.queue = []
		# Index of the currently playing track.
		self.playing_track = 0
		# Status of the player.
		self.stopped = True
		# Modify some default settings present in Bass so it will increase timeout connection, thus causing less "connection timed out" errors when playing.
		bassconfig = BassConfig()
		# Set timeout connection to 30 seconds.
		bassconfig["net_timeout"] = 30000
		pub.subscribe(self.play, "play")
		pub.subscribe(self.play_all, "play-all")
		pub.subscribe(self.pause, "pause")
		pub.subscribe(self.stop, "stop")
		pub.subscribe(self.play_next, "play_next")
		pub.subscribe(self.play_previous, "play_previous")

	def play(self, object, set_info=True, fresh=False):
		""" Play an URl Stream.
		@object dict: typically an audio object as returned by VK, with a "url" component which must be a valid URL to a media file.
		@set_info bool: If true, will set information about the currently playing audio in the application status bar.
		@fresh bool: If True, will remove everything playing in the queue and start this file only. otherwise it will play the new file but not remove the current queue."""
		if "url" in object and object["url"] =="":
			pub.sendMessage("notify", message=_("This file could not be played because it is not allowed in your country"))
			return
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
			url_ = bytes(object["url"], "utf-8")
			try:
				self.stream = URLStream(url=url_)
			except IndexError:
				log.error("Unable to play URL %s" % (url_))
				return
			# Translators: {0} will be replaced with a song's title and {1} with the artist.
			if set_info:
				msg = _("Playing {0} by {1}").format(object["title"], object["artist"])
				pub.sendMessage("update-status-bar", status=msg)
			self.stream.volume = self.vol/100.0
			self.stream.play()
			self.stopped = False
			self.is_working = False

	def stop(self):
		""" Stop audio playback. """
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
			self.stopped = True
		if hasattr(self, "worker") and self.worker != None:
			self.worker.cancel()
			self.worker = None
			self.queue = []

	def pause(self):
		""" pause the current playback, without destroying the queue or the current stream. If the stream is already paused this function will resume  the playback. """
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
		elif vol < 0:
			self.vol = 0
		elif vol > 100:
			self.vol = 100
		if self.stream != None:
			self.stream.volume = self.vol/100.0

	def play_all(self, list_of_songs, shuffle=False):
		""" Play all passed songs and adds all of those to the queue.
		@list_of_songs list: A list of audio objects returned by VK.
		@shuffle bool: If True, the files will be played randomly."""
		self.playing_track = 0
		self.stop()
		# Skip all country restricted tracks as they are not playable here.
		self.queue = [i for i in list_of_songs if i["url"] != ""]
		if shuffle:
			random.shuffle(self.queue)
		self.play(self.queue[self.playing_track])
		self.worker = RepeatingTimer(5, self.player_function)
		self.worker.start()

	def player_function(self):
		""" Check if the stream has reached the end of the file  so it will play the next song. """
		if self.stream != None and self.stream.is_playing == False and self.stopped == False and len(self.stream) == self.stream.position:
			if len(self.queue) == 0 or self.playing_track >= len(self.queue):
				self.worker.cancel()
				return
			if self.playing_track < len(self.queue):
				self.playing_track += 1
			self.play(self.queue[self.playing_track])

	def play_next(self):
		""" Play the next song in the queue. """
		if len(self.queue) == 0:
			return
		if self.playing_track < len(self.queue)-1:
			self.playing_track += 1
		else:
			self.playing_track = 0
		self.play(self.queue[self.playing_track])

	def play_previous(self):
		""" Play the previous song in the queue. """
		if len(self.queue) == 0:
			return
		if self.playing_track <= 0:
			self.playing_track = len(self.queue)-1
		else:
			self.playing_track -= 1
		self.play(self.queue[self.playing_track])

	def check_is_playing(self):
		""" check if the player is already playing a stream. """
		if self.stream == None:
			return False
		if self.stream != None and self.stream.is_playing == False:
			return False
		else:
			return True

