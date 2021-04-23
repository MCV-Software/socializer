# -*- coding: utf-8 -*-
import logging
import wx
import widgetUtils
import output
from wxUI.tabs import videoAlbum
from .video import videoBuffer

log = logging.getLogger("controller.buffers")

class videoAlbumBuffer(videoBuffer):

	def create_tab(self, parent):
		self.tab = video.videoAlbumTab(parent)
		self.tab.play.Enable(False)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		super(videoAlbumBuffer, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_album)

	def load_album(self, *args, **kwargs):
		output.speak(_("Loading album..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)
		self.tab.play.Enable(True)