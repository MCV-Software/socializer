# -*- coding: utf-8 -*-
import wx
import widgetUtils
from .home import homeTab

class communityBoardTab(homeTab):
    def create_list(self):
        self.lbl = wx.StaticText(self, wx.NewId(), _("Topics"))
        self.list = widgetUtils.list(self, *[_("User"), _("Title"), _("Posts"), _("Last")], style=wx.LC_REPORT)
        self.list.set_windows_size(0, 200)
        self.list.set_windows_size(1, 64)
        self.list.set_windows_size(2, 15)
        self.list.set_windows_size(2, 250)
        self.list.set_size()
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)
