# -*- coding: utf-8 -*-
import logging
import webbrowser
import wx
import widgetUtils
import output
from wxUI.tabs import video
from wxUI import commonMessages, menus
from controller import selector
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.video")

class videoBuffer(wallBuffer):
	""" This buffer represents video elements, and it can be used for showing videos for the logged user or someone else."""

	def create_tab(self, parent):
		self.tab = video.videoTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		super(videoBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		""" Due to inheritance this method should be called play_audio, but play the currently focused video.
		Opens a webbrowser pointing to the video's URL."""
		selected = self.tab.list.get_selected()
		if self.tab.list.get_count() == 0:
			return
		if selected == -1:
			selected = 0
		output.speak(_("Opening video in webbrowser..."))
		webbrowser.open_new_tab(self.session.db[self.name]["items"][selected]["player"])
#		print self.session.db[self.name]["items"][selected]
		return True

	def open_post(self, *args, **kwargs):
				pass

	def remove_buffer(self, mandatory=False):
		if "me_video" == self.name:
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
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["video_id"] = post["id"]
		if "album_id" in post:
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		video = self.session.vk.client.video.add(**args)
		if video != None and int(video) > 21:
			output.speak(_("Video added to your library"))

	def remove_from_library(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["video_id"] = post["id"]
		args["owner_id"] = self.session.user_id
		result = self.session.vk.client.video.delete(**args)
		if int(result) == 1:
			output.speak(_("Removed video from library"))
			self.tab.list.remove_item(self.tab.list.get_selected())

	def move_to_album(self, *args, **kwargs):
		if len(self.session.video_albums) == 0:
			return commonMessages.no_video_albums()
		post= self.get_post()
		if post == None:
			return
		album = selector.album(_("Select the album where you want to move this video"), self.session, "video_albums")
		if album.item == None: return
		id = post["id"]
		response = self.session.vk.client.video.addToAlbum(album_ids=album.item, video_id=id, target_id=self.session.user_id, owner_id=self.get_post()["owner_id"])
		if response == 1:
		# Translators: Used when the user has moved an video  to an album.
			output.speak(_("Moved"))

	def get_menu(self):
		""" We'll use the same menu that is used for audio items, as the options are exactly the same"""
		p = self.get_post()
		if p == None:
			return
		m = menus.audioMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_("&Remove"))
			widgetUtils.connect_event(m, widgetUtils.MENU, self.remove_from_library, menuitem=m.library)
		else:
			widgetUtils.connect_event(m, widgetUtils.MENU, self.add_to_library, menuitem=m.library)
		return m

	def open_in_browser(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		url = "https://vk.com/video{user_id}_{video_id}".format(user_id=post["owner_id"], video_id=post["id"])
		webbrowser.open_new_tab(url)