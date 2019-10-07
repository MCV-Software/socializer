# -*- coding: utf-8 -*-
""" Audio player module for socializer.
As this player does not have (still) an associated GUI, I have decided to place here the code for the interactor, which connects a bunch of pubsub events, and the presenter itself.
"""
import sys
import time
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
from mysc.thread_utils import call_threaded
from sessionmanager import utils

player = None
log = logging.getLogger("player")

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
		self.message = None
		self.vol = config.app["sound"]["volume"]
		# this variable is set to true when the URLPlayer is decoding something, thus it will block other calls to the play method.
		self.is_working = False
		# Playback queue.
		self.queue = []
		# Index of the currently playing track.
		self.playing_track = 0
		self.playing_all = False
		self.worker = RepeatingTimer(5, self.player_function)
		self.worker.start()
		# Status of the player.
		self.stopped = True
		# Modify some default settings present in Bass so it will increase timeout connection, thus causing less "connection timed out" errors when playing.
		bassconfig = BassConfig()
		# Set timeout connection to 30 seconds.
		bassconfig["net_timeout"] = 30000
		# subscribe all pubsub events.
		pub.subscribe(self.play, "play")
		pub.subscribe(self.play_message, "play-message")
		pub.subscribe(self.play_all, "play-all")
		pub.subscribe(self.pause, "pause")
		pub.subscribe(self.stop, "stop")
		pub.subscribe(self.play_next, "play-next")
		pub.subscribe(self.play_previous, "play-previous")
		pub.subscribe(self.seek, "seek")

	# Stopped has a special function here, hence the decorator
	# when stopped will be set to True, it will send a pubsub event to inform other parts of the application about the status change.
	# this is useful for changing labels between play and pause, and so on, in buttons.
	@property
	def stopped(self):
		return self._stopped

	@stopped.setter
	def stopped(self, value):
		self._stopped = value
		pub.sendMessage("playback-changed", stopped=value)

	def play(self, object, set_info=True, fresh=False):
		""" Play an URl Stream.
		@object dict: typically an audio object as returned by VK, with a "url" component which must be a valid URL to a media file.
		@set_info bool: If true, will set information about the currently playing audio in the application status bar.
		@fresh bool: If True, will remove everything playing in the queue and start this file only. otherwise it will play the new file but not remove the current queue."""
		if "url" in object and object["url"] =="":
			pub.sendMessage("notify", message=_("This file could not be played because it is not allowed in your country"))
			return
		if self.stream != None and (self.stream.is_playing == True or self.stream.is_stalled == True):
			try:
				self.stream.stop()
			except BassError:
				log.exception("error when stopping the file")
				self.stream = None
			self.stopped = True
			if fresh == True:
				self.queue = []
		# Make sure that  there are no other sounds trying to be played.
		if self.is_working == False:
			self.is_working = True
			# Let's encode the URL as bytes if on Python 3
			url_ = utils.transform_audio_url(object["url"])
			url_ = bytes(url_, "utf-8")
			try:
				self.stream = URLStream(url=url_)
			except:
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

	def play_message(self, message_url):
		if self.message != None and (self.message.is_playing == True or self.message.is_stalled == True):
			return self.stop_message()
		output.speak(_("Playing..."))
		url_ = utils.transform_audio_url(message_url)
		url_ = bytes(url_, "utf-8")
		try:
			self.message = URLStream(url=url_)
		except:
			log.error("Unable to play URL %s" % (url_))
			return
			self.message.volume = self.vol/100.0
		self.message.play()
		volume_percent = self.volume*0.25
		volume_step = self.volume*0.15
		while self.stream.volume*100 > volume_percent:
			self.stream.volume = self.stream.volume-(volume_step/100)
			time.sleep(0.1)

	def stop(self):
		""" Stop audio playback. """
		if self.stream != None and self.stream.is_playing == True:
			self.stream.stop()
			self.stopped = True
			self.queue = []

	def stop_message(self):
		if hasattr(self, "message") and self.message != None and self.message.is_playing == True:
			self.message.stop()
			volume_step = self.volume*0.15
			while self.stream.volume*100 < self.volume:
				self.stream.volume = self.stream.volume+(volume_step/100)
				time.sleep(0.1)
			self.message = None

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
				if self.playing_all == False and len(self.queue) > 0:
					self.playing_all = True

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
			if self.message != None and self.message.is_playing:
				self.stream.volume = (self.vol*0.25)/100.0
				self.message.volume = self.vol/100.0
			else:
				self.stream.volume = self.vol/100.0

	def play_all(self, list_of_songs, shuffle=False):
		""" Play all passed songs and adds all of those to the queue.
		@list_of_songs list: A list of audio objects returned by VK.
		@shuffle bool: If True, the files will be played randomly."""
		if self.is_working:
			return
		self.playing_track = 0
		self.stop()
		# Skip all country restricted tracks as they are not playable here.
		self.queue = [i for i in list_of_songs if i["url"] != ""]
		if shuffle:
			random.shuffle(self.queue)
		call_threaded(self.play, self.queue[self.playing_track])
		self.playing_all = True

	def player_function(self):
		""" Check if the stream has reached the end of the file  so it will play the next song. """
		if self.message != None and self.message.is_playing == False and len(self.message) == self.message.position:
			volume_step = self.volume*0.15
			while self.stream != None and self.stream.volume*100 < self.volume:
				self.stream.volume = self.stream.volume+(volume_step/100)
				time.sleep(0.1)
		if self.stream != None and self.stream.is_playing == False and self.stopped == False and len(self.stream) == self.stream.position:
			if self.playing_track >= len(self.queue):
				self.stopped = True
				self.playing_all = False
				return
			elif self.playing_all == False:
				self.stopped = True
				return
			elif self.playing_track < len(self.queue):
				self.playing_track += 1
			self.play(self.queue[self.playing_track])

	def play_next(self):
		""" Play the next song in the queue. """
		if len(self.queue) == 0:
			return
		if self.is_working:
			return
		if self.playing_track < len(self.queue)-1:
			self.playing_track += 1
		else:
			self.playing_track = 0
		call_threaded(self.play, self.queue[self.playing_track])

	def play_previous(self):
		""" Play the previous song in the queue. """
		if len(self.queue) == 0:
			return
		if self.is_working:
			return
		if self.playing_track <= 0:
			self.playing_track = len(self.queue)-1
		else:
			self.playing_track -= 1
		call_threaded(self.play, self.queue[self.playing_track])

	def seek(self, ms=0):
		if self.check_is_playing():
			if self.stream.position < 500000 and ms < 0:
				self.stream.position = 0
			else:
				try:
					self.stream.position = self.stream.position+ms
				except:
					pass

	def check_is_playing(self):
		""" check if the player is already playing a stream. """
		if self.stream == None:
			return False
		if self.stream != None and self.stream.is_playing == False and self.stream.is_stalled == False:
			return False
		else:
			return True