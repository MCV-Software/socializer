# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub

class homeTab(wx.Panel):

	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Posts"))
		self.list = widgetUtils.list(self, *[_(u"User"), _(u"Text"), _(u"Date")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 80)
		self.list.set_windows_size(1, 190)
		self.list.set_windows_size(2, 40)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"Post"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)

	def __init__(self, parent):
		super(homeTab, self).__init__(parent=parent)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_post_buttons()
		sizer.Add(self.postBox, 0, wx.ALL, 5)
		self.create_list()
		sizer.Add(self.lbl, 0, wx.ALL, 5)
		sizer.Add(self.list.list, 0, wx.ALL, 5)
		self.SetSizer(sizer)

	def OnKeyDown(self, ev=None):
		pub.sendMessage("show-current-status", buffer=self.name)
		ev.Skip()

	def showMenu(self, ev):
		if self.results.get_count() == 0: return
		pub.sendMessage("show-menu", position=ev.GetPosition())

	def showMenuByKey(self, ev):
		if self.results.get_count() == 0: return
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			pub.sendMessage("show-menu", position=self.results.list.GetPosition())

class feedTab(homeTab):
	def __init__(self, parent):
		super(feedTab, self).__init__(parent=parent)
		self.name = "me_feed"

class audioTab(homeTab):
	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Music"))
		self.list = widgetUtils.list(self, *[_(u"Title"), _(u"Artist"), _(u"Duration")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 80)
		self.list.set_windows_size(1, 190)
		self.list.set_windows_size(2, 40)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"Post"))
		self.play = wx.Button(self, -1, _(u"Play"))
		self.play_all = wx.Button(self, -1, _(u"Play All"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.play, 0, wx.ALL, 5)
		self.postBox.Add(self.play_all, 0, wx.ALL, 5)

class notificationsTab(homeTab):
	def __init__(self, parent):
		super(notificationsTab, self).__init__(parent=parent)
		self.name = "notifications"

	def OnKeyDown(self, ev=None):
		pub.sendMessage("show-notification", buffer=self.name)
		ev.Skip()

	def create_list(self):
		self.list = widgetUtils.list(self, *[_(u"Notification")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 190)
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

class albumTab(homeTab):
	def __init__(self, parent):
		super(albumTab, self).__init__(parent=parent)
		self.name = "albums"

	def OnKeyDown(self, ev=None):
		pub.sendMessage("show-album", buffer=self.name)
		ev.Skip()

	def create_list(self):
		self.list = widgetUtils.list(self, *[_(u"User"), _(u"Name"), _(u"Description"), _(u"Photos"), _(u"Created at")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 190)
		self.list.set_windows_size(1, 320)
		self.list.set_windows_size(2, 513)
		self.list.set_windows_size(3, 390)
		self.list.set_windows_size(4, 180)
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

class friendsTab(homeTab):
	def OnKeyDown(self, ev=None):
		pub.sendMessage("show-album", buffer=self.name)
		ev.Skip()

	def create_list(self):
		self.list = widgetUtils.list(self, *[_(u"Name")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 400)
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

