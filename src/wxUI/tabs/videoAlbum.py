# -*- coding: utf-8 -*-
import wx
from .video import videoTab

class videoAlbumTab(videoTab):

    def create_post_buttons(self):
        self.postBox = wx.BoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
        self.load = wx.Button(self.postBox.GetStaticBox(), wx.NewId(), _("Load buffer"))
        self.post = wx.Button(self.postBox.GetStaticBox(), -1, _("&Post"))
        self.play = wx.Button(self.postBox.GetStaticBox(), -1, _("P&lay"))
        self.postBox.Add(self.post, 0, wx.ALL, 5)
        self.postBox.Add(self.play, 0, wx.ALL, 5)
