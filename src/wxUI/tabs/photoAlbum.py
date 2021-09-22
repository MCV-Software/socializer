# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub
from .home import homeTab

class albumTab(homeTab):
    def __init__(self, parent):
        super(albumTab, self).__init__(parent=parent)
        self.name = "albums"

    def OnKeyDown(self, ev=None):
        pub.sendMessage("show-album", buffer=self.name)
        ev.Skip()

    def create_list(self):
        self.list = widgetUtils.list(self, *[_("User"), _("Name"), _("Description"), _("Photos"), _("Created at")], style=wx.LC_REPORT)
        self.list.set_windows_size(0, 190)
        self.list.set_windows_size(1, 320)
        self.list.set_windows_size(2, 513)
        self.list.set_windows_size(3, 390)
        self.list.set_windows_size(4, 180)
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)
