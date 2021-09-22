# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub
from .home import homeTab

class peopleTab(homeTab):

    def create_list(self):
        self.lbl = wx.StaticText(self, wx.NewId(), _("Friends"))
        self.list = widgetUtils.list(self, *[_("Name"), _("Last seen")], style=wx.LC_REPORT)
        self.list.set_windows_size(0, 190)
        self.list.set_windows_size(1, 100)
        self.list.set_size()
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

    def create_post_buttons(self):
        self.postBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
        self.post = wx.Button(self.postBox.GetStaticBox(), -1, _("&Post on user's wall"))
        self.new_chat = wx.Button(self.postBox.GetStaticBox(), wx.NewId(), _("Send message"))
        self.postBox.Add(self.post, 0, wx.ALL, 5)
        self.postBox.Add(self.new_chat, 0, wx.ALL, 5)
