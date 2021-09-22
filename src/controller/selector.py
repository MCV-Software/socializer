# -*- coding: utf-8 -*-
import widgetUtils
from wxUI.dialogs import selector as gui

class album(object):

    def __init__(self, title, session, album_type="audio_albums"):
        super(album, self).__init__()
        self.item = None
        self.session = session
        if not hasattr(self.session, album_type):
            return
        self.albums = getattr(self.session, album_type)
        self.dialog = gui.selectAlbum(title=title, albums=self.get_albums_as_string())
        response = self.dialog.get_response()
        if response == widgetUtils.OK:
            self.item = self.search_item(self.dialog.get_string())

    def get_albums_as_string(self):
        return [i["title"] for i in self.albums]

    def search_item(self, item):
        for i in self.albums:
            if i["title"] == item:
                return i["id"]
        return None
