# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub
from .home import homeTab

class notificationTab(homeTab):
    def OnKeyDown(self, ev=None):
        pub.sendMessage("show-notification", buffer=self.name)
        ev.Skip()

    def create_list(self):
        self.lbl = wx.StaticText(self, wx.NewId(), _("Po&sts"))
        self.list = widgetUtils.list(self, *[_("Notification"), _("Date")], style=wx.LC_REPORT)
        self.list.set_windows_size(0, 190)
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)
