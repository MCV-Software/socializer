# -*- coding: utf-8 -*-
import logging
from sessionmanager import utils
from pubsub import pub
from mysc.thread_utils import call_threaded
from presenters import base, player

log = logging.getLogger(__file__)

class displayAudioPresenter(base.basePresenter):
	def __init__(self, session, postObject, view, interactor):
		super(displayAudioPresenter, self).__init__(view=view, interactor=interactor, modulename="display_audio")
		self.added_audios = {}
		self.session = session
		self.post = postObject
		self.load_audios()
		self.fill_information(0)
		self.run()

	def add_to_library(self, audio_index):
		post = self.post[audio_index]
		args = {}
		args["audio_id"] = post["id"]
		if "album_id" in post:
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			self.added_audios[post["id"]] = audio
			self.send_message("disable_control", control="add")
			self.send_message("enable_control", control="remove")

	def remove_from_library(self, audio_index):
		post = self.post[audio_index]
		args = {}
		if post["id"] in self.added_audios:
			args["audio_id"] = self.added_audios[post["id"]]
			args["owner_id"] = self.session.user_id
		else:
			args["audio_id"] = post["id"]
			args["owner_id"] = post["owner_id"]
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			self.send_message("enable_control", control="add")
			self.send_message("disable_control", control="remove")
			if post["id"] in self.added_audios:
				self.added_audios.pop(post["id"])

	def fill_information(self, index):
		post = self.post[index]
		if "artist" in post:
			self.send_message("set", control="artist", value=post["artist"])
		if "title" in post:
			self.send_message("set", control="title", value=post["title"])
		if "duration" in post:
			self.send_message("set", control="duration", value=utils.seconds_to_string(post["duration"]))
		self.send_message("set_title", value="{0} - {1}".format(post["title"], post["artist"]))
		call_threaded(self.get_lyrics, index)
		if  post["owner_id"] == self.session.user_id or (post["id"] in self.added_audios) == True:
			self.send_message("enable_control", control="remove")
			self.send_message("disable_control", control="add")
		else:
			self.send_message("enable_control", control="add")
			self.send_message("disable_control", control="remove")

	def get_lyrics(self, audio_index):
		post = self.post[audio_index]
		if "lyrics_id" in post:
			l = self.session.vk.client.audio.getLyrics(lyrics_id=int(post["lyrics_id"]))
			self.send_message("set", control="lyric", value=l["text"])
		else:
			self.send_message("disable_control", control="lyric")

	def get_suggested_filename(self, audio_index):
		post = self.post[audio_index]
		return utils.safe_filename("{0} - {1}.mp3".format(post["title"], post["artist"]))

	def download(self, audio_index, path):
		post = self.post[audio_index]
		if path != None:
			pub.sendMessage("download-file", url=post["url"], filename=path)

	def play(self, audio_index):
		post = self.post[audio_index]
		if player.player.check_is_playing() == True:
			return pub.sendMessage("stop")
		pub.sendMessage("play", object=post)

	def load_audios(self):
		audios = []
		for i in self.post:
			s = "{0} - {1}. {2}".format(i["title"], i["artist"], utils.seconds_to_string(i["duration"]))
			audios.append(s)
		self.send_message("add_items", control="list", items=audios)
		if len(self.post) == 1:
			self.send_message("disable_control", control="list")
			self.send_message("focus_control", control="title")

	def handle_changes(self, audio_index):
		self.fill_information(audio_index)