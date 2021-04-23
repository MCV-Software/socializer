# -*- coding: utf-8 -*-
import os
import logging
import webbrowser
import wx
import presenters
import views
import interactors
import widgetUtils
from pubsub import pub
from vk_api import upload
from mutagen.id3 import ID3
from presenters import player
from wxUI.tabs import audio
from sessionmanager import utils
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus
from controller import selector
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.audio")

class audioBuffer(wallBuffer):
	def create_tab(self, parent):
		self.tab = audio.audioTab(parent)
		self.tab.name = self.name
		self.connect_events()
		if self.name == "me_audio":
			self.tab.post.Enable(True)

	def get_event(self, ev):
		if ev.GetKeyCode() == wx.WXK_RETURN:
			if len(self.tab.list.get_multiple_selection()) < 2:
				event = "play_all"
			else:
				event = "play_audio"
		else:
			event = None
			ev.Skip()
		if event != None:
			try:
				getattr(self, event)(skip_pause=True)
			except AttributeError:
				pass

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		widgetUtils.connect_event(self.tab.play_all, widgetUtils.BUTTON_PRESSED, self.play_all)
		pub.subscribe(self.change_label, "playback-changed")
		super(audioBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		if player.player.check_is_playing() and not "skip_pause" in kwargs:
			return pub.sendMessage("pause")
		selected = self.tab.list.get_multiple_selection()
		if len(selected) == 0:
			return
		elif len(selected) == 1:
			pub.sendMessage("play", object=self.session.db[self.name]["items"][selected[0]])
		else:
			selected_audios = [self.session.db[self.name]["items"][item] for item in selected]
			pub.sendMessage("play-all", list_of_songs=selected_audios)
		return True

	def play_next(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected < 0:
			selected = 0
		if self.tab.list.get_count() <= selected+1:
			newpos = 0
		else:
			newpos = selected+1
		self.tab.list.select_item(newpos)
		self.play_audio()

	def play_previous(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected <= 0:
			selected = self.tab.list.get_count()
		newpos = selected-1
		self.tab.list.select_item(newpos)
		self.play_audio()

	def open_post(self, *args, **kwargs):
		selected = self.tab.list.get_multiple_selection()
		if len(selected) < 1:
			return
		audios = [self.session.db[self.name]["items"][audio] for audio in selected]
		a = presenters.displayAudioPresenter(session=self.session, postObject=audios, interactor=interactors.displayAudioInteractor(), view=views.displayAudio())

	def play_all(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		if self.name not in self.session.db:
			return
		audios = [i for i in self.session.db[self.name]["items"][selected:]]
		pub.sendMessage("play-all", list_of_songs=audios)
		return True

	def remove_buffer(self, mandatory=False):
		if "me_audio" == self.name or "popular_audio" == self.name or "recommended_audio" == self.name:
			output.speak(_("This buffer can't be deleted"))
			return False
		else:
			if mandatory == False:
				dlg = commonMessages.remove_buffer()
			else:
				dlg = widgetUtils.YES
			if dlg == widgetUtils.YES:
				self.session.db.pop(self.name)
				return True
			else:
				return False

	def get_more_items(self, *args, **kwargs):
		# Translators: Some buffers can't use the get previous item feature due to API limitations.
		output.speak(_("This buffer doesn't support getting more items."))

	def onFocus(self, event, *args, **kwargs):
		event.Skip()

	def add_to_library(self, *args, **kwargs):
		call_threaded(self._add_to_library, *args, **kwargs)

	def _add_to_library(self, *args, **kwargs):
		selected = self.tab.list.get_multiple_selection()
		if len(selected) < 1:
			return
		audios = [self.session.db[self.name]["items"][audio] for audio in selected]
		errors_detected = 0
		for i in audios:
			args = {}
			args["audio_id"] = i["id"]
			if "album_id" in i:
				args["album_id"] = i["album_id"]
			args["owner_id"] = i["owner_id"]
			try:
				audio = self.session.vk.client.audio.add(**args)
			except VkApiError:
				errors_detected = errors_detected + 1
				continue
			if audio != None and int(audio) < 21:
				errors_detected = errors_detected + 1
		if errors_detected == 0:
			if len(selected) == 1:
				msg = _("Audio added to your library")
			elif len(selected) > 1 and len(selected) < 5:
				msg = _("{0} audios were added to your library.").format(len(selected),)
			else:
				msg = _("{audios} audios were added to your library.").format(audios=len(selected),)
			output.speak(msg)
		else:
			output.speak(_("{0} errors occurred while attempting to add {1} audios to your library.").format(errors_detected, len(selected)))

	def remove_from_library(self, *args, **kwargs):
		call_threaded(self._remove_from_library, *args, **kwargs)

	def _remove_from_library(self, *args, **kwargs):
		selected = self.tab.list.get_multiple_selection()
		if len(selected) < 1:
			return
		audios = [self.session.db[self.name]["items"][audio] for audio in selected]
		errors_detected = 0
		audios_removed = 0
		for i in range(0, len(selected)):
			args = {}
			args["audio_id"] = audios[i]["id"]
			args["owner_id"] = self.session.user_id
			result = self.session.vk.client.audio.delete(**args)
			if int(result) != 1:
				errors_dtected = errors_detected + 1
			else:
				self.session.db[self.name]["items"].pop(selected[i]-audios_removed)
				self.tab.list.remove_item(selected[i]-audios_removed)
				audios_removed = audios_removed + 1 
		if errors_detected == 0:
			if len(selected) == 1:
				msg = _("Audio removed.")
			elif len(selected) > 1 and len(selected) < 5:
				msg = _("{0} audios were removed.").format(len(selected),)
			else:
				msg = _("{audios} audios were removed.").format(audios=len(selected),)
			output.speak(msg)
		else:
			output.speak(_("{0} errors occurred while attempting to remove {1} audios.").format(errors_detected, len(selected)))

	def move_to_album(self, *args, **kwargs):
		if len(self.session.audio_albums) == 0:
			return commonMessages.no_audio_albums()
		album = selector.album(_("Select the album where you want to move this song"), self.session)
		if album.item == None:
			return
		call_threaded(self._move_to_album, album.item, *args, **kwargs)

	def _move_to_album(self, album, *args, **kwargs):
		selected = self.tab.list.get_multiple_selection()
		if len(selected) < 1:
			return
		audios = [self.session.db[self.name]["items"][audio] for audio in selected]
		errors_detected = 0
		for i in audios:
			id = i["id"]
			try:
				response = self.session.vk.client.audio.add(playlist_id=album, audio_id=id, owner_id=i["owner_id"])
			except VkApiError:
				errors_detected = errors_detected + 1
		if errors_detected == 0:
			if len(selected) == 1:
				msg = _("Audio added to playlist.")
			elif len(selected) > 1 and len(selected) < 5:
				msg = _("{0} audios were added to playlist.").format(len(selected),)
			else:
				msg = _("{audios} audios were added to playlist.").format(audios=len(selected),)
			output.speak(msg)
		else:
			output.speak(_("{0} errors occurred while attempting to add {1} audios to your playlist.").format(errors_detected, len(selected)))

	def get_menu(self):
		p = self.get_post()
		if p == None:
			return
		m = menus.audioMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.play_audio, menuitem=m.play)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.download, menuitem=m.download)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.select_all, menuitem=m.select)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.deselect_all, menuitem=m.deselect)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_("&Remove"))
			widgetUtils.connect_event(m, widgetUtils.MENU, self.remove_from_library, menuitem=m.library)
		else:
			widgetUtils.connect_event(m, widgetUtils.MENU, self.add_to_library, menuitem=m.library)
		return m

	def post(self, *args, **kwargs):
		""" Uploads an audio to the current user's library from the computer. """
		file = self.tab.get_file_to_upload()
		if file == None:
			return
		audio_tags = ID3(file)
		if "TIT2" in audio_tags:
			title = audio_tags["TIT2"].text[0]
		else:
			title = _("Untitled")
		if "TPE1" in audio_tags:
			artist = audio_tags["TPE1"].text[0]
		else:
			artist = _("Unknown artist")
		uploader = upload.VkUpload(self.session.vk.session_object)
		call_threaded(uploader.audio, file, title=title, artist=artist)

	def open_in_browser(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		url = "https://vk.com/audio{user_id}_{post_id}".format(user_id=post["owner_id"], post_id=post["id"])
		webbrowser.open_new_tab(url)

	def change_label(self, stopped):
		if hasattr(self.tab, "play"):
			if stopped == False:
				self.tab.play.SetLabel(_("P&ause"))
			else:
				self.tab.play.SetLabel(_("P&lay"))

	def __del__(self):
		pub.unsubscribe(self.change_label, "playback-changed")

	def download(self, *args, **kwargs):
		selected = self.tab.list.get_multiple_selection()
		if len(selected) < 1:
			return
		audios = [self.session.db[self.name]["items"][audio] for audio in selected]
		if len(audios) == 0:
			return
		elif len(audios) == 1:
			multiple = False
			filename = utils.safe_filename("{0} - {1}.mp3".format(audios[0]["title"], audios[0]["artist"]))
		else:
			multiple = True
			filename = "" # No default filename for multiple files.
		path = self.tab.get_download_path(filename=filename, multiple=multiple)
		self.download_threaded(path, multiple, audios)

	def download_threaded(self, path, multiple, audios):
		if multiple == False:
			url = audios[0]["url"]
			pub.sendMessage("download-file", url=url, filename=path)
			return
		else:
			downloads = []
			for i in audios:
				filename = utils.safe_filename("{0} - {1}.mp3".format(i["title"], i["artist"]))
				filepath = os.path.join(path, filename)
				downloads.append((utils.transform_audio_url(i["url"]), filepath))
				pub.sendMessage("download-files", downloads=downloads)

	def select_all(self, *args, **kwargs):
		items = self.tab.list.list.GetItemCount()
		for i in range(0, items):
			self.tab.list.list.SetItemImage(i, 1)

	def deselect_all(self, *args, **kwargs):
		items = self.tab.list.list.GetItemCount()
		for i in range(0, items):
			self.tab.list.list.SetItemImage(i, 0)