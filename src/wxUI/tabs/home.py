# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub

class homeTab(wx.Panel):

	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _("Po&sts"))
		self.list = widgetUtils.list(self, *[_("User"), _("Text"), _("Date")], style=wx.LC_REPORT, name=_("Posts"))
		self.list.set_windows_size(0, 200)
		self.list.set_windows_size(1, 300)
		self.list.set_windows_size(2, 250)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.postBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
		self.post = wx.Button(self.postBox.GetStaticBox(), wx.NewId(), _("&Post"))
		self.postBox.Add(self.post, 0, wx.ALL, 5)

	def __init__(self, parent):
		super(homeTab, self).__init__(parent=parent)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_list()
		self.create_post_buttons()
		sizer.Add(self.postBox, 0, wx.ALL, 5)
		sizer.Add(self.lbl, 0, wx.ALL, 5)
		sizer.Add(self.list.list, 1, wx.EXPAND, 5)
		self.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def OnKeyDown(self, ev=None):
		pub.sendMessage("show-current-status", buffer=self.name)
		ev.Skip()

	def showMenu(self, ev):
		if self.list.get_count() == 0: return
		pub.sendMessage("show-menu", position=ev.GetPosition())

	def showMenuByKey(self, ev):
		if self.list.get_count() == 0: return
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			pub.sendMessage("show-menu", position=self.results.list.GetPosition())

	def set_focus_function(self, focus_function):
		self.list.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, focus_function)