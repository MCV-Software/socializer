# -*- coding: utf-8 -*-
import wx
from .audio import audioTab

class audioAlbumTab(audioTab):

    def create_post_buttons(self):
        self.postBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
        self.load = wx.Button(self.postBox.GetStaticBox(), wx.NewId(), _("Load buffer"))
        self.post = wx.Button(self.postBox.GetStaticBox(), -1, _("&Post"))
        self.play = wx.Button(self.postBox.GetStaticBox(), -1, _("P&lay"))
        self.play_all = wx.Button(self.postBox.GetStaticBox(), -1, _("Play &All"))
        self.postBox.Add(self.load, 0, wx.ALL, 5)
        self.postBox.Add(self.post, 0, wx.ALL, 5)
        self.postBox.Add(self.play, 0, wx.ALL, 5)
        self.postBox.Add(self.play_all, 0, wx.ALL, 5)
