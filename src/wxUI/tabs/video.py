# -*- coding: utf-8 -*-
import wx
import widgetUtils
from .home import homeTab

class videoTab(homeTab):
	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _("Video&s"))
		self.list = widgetUtils.list(self, *[_("Title"), _("Description"), _("Duration")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 160)
		self.list.set_windows_size(1, 380)
		self.list.set_windows_size(2, 80)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.postBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
		self.post = wx.Button(self.postBox.GetStaticBox(), -1, _("&Post"))
		self.play = wx.Button(self.postBox.GetStaticBox(), -1, _("P&lay"))
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.play, 0, wx.ALL, 5)