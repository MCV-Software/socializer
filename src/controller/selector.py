# -*- coding: utf-8 -*-
import widgetUtils
from wxUI.dialogs import selector as gui

class audioAlbum(object):

	def __init__(self, title, session):
		super(audioAlbum, self).__init__()
		self.item = None
		self.session = session
		self.dialog = gui.selectAlbum(title=title, albums=self.get_albums_as_string())
		response = self.dialog.get_response()
		if response == widgetUtils.OK:
			self.item = self.search_item(self.dialog.get_string())

	def get_albums_as_string(self):
		return [i["title"] for i in self.session.audio_albums]

	def search_item(self, item):
		for i in self.session.audio_albums:
			if i["title"] == item:
				return i["id"]
		return None
