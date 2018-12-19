# -*- coding: utf-8 -*-
import wx
import widgetUtils
from pubsub import pub

class homeTab(wx.Panel):

	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Po&sts"))
		self.list = widgetUtils.list(self, *[_(u"User"), _(u"Text"), _(u"Date")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 200)
		self.list.set_windows_size(1, 300)
		self.list.set_windows_size(2, 250)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)

	def __init__(self, parent):
		super(homeTab, self).__init__(parent=parent)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_post_buttons()
		sizer.Add(self.postBox, 0, wx.ALL, 5)
		self.create_list()
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

class feedTab(homeTab):
	def __init__(self, parent):
		super(feedTab, self).__init__(parent=parent)
		self.name = "me_feed"

class audioTab(homeTab):
	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Mu&sic"))
		self.list = widgetUtils.list(self, *[_(u"Title"), _(u"Artist"), _(u"Duration")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 160)
		self.list.set_windows_size(1, 380)
		self.list.set_windows_size(2, 80)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.play = wx.Button(self, -1, _(u"P&lay"))
		self.play_all = wx.Button(self, -1, _(u"Play &All"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.play, 0, wx.ALL, 5)
		self.postBox.Add(self.play_all, 0, wx.ALL, 5)

class audioAlbumTab(audioTab):

	def create_post_buttons(self):
		self.load = wx.Button(self, wx.NewId(), _(u"Load album"))
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.play = wx.Button(self, -1, _(u"P&lay"))
		self.play_all = wx.Button(self, -1, _(u"Play &All"))
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

class empty(wx.Panel):
	def __init__(self, parent, name):
		super(empty, self).__init__(parent=parent, name=name)
		self.name = name
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)

class chatTab(wx.Panel):

	def insert_attachments(self, attachments):
		for i in attachments:
			self.attachments.insert_item(False, *i)

	def __init__(self, parent):
		super(chatTab, self).__init__(parent=parent)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.create_controls())
		sizer.Add(self.create_attachments(), 0, wx.ALL, 5)
		sizer.Add(self.create_chat(), 0, wx.ALL, 5)
		self.attachment = wx.Button(self, wx.NewId(), _(u"Add"))
		sizer.Add(self.attachment, 0, wx.ALL, 5)
		self.send = wx.Button(self, -1, _(u"Send"))
		sizer.Add(self.send, 0, wx.ALL, 5)
		self.SetSizer(sizer)

	def create_controls(self):
		lbl1 = wx.StaticText(self, wx.NewId(), _(u"History"))
		self.history = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE, size=(500, 300))
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl1, 0, wx.ALL, 5)
		box.Add(self.history, 0, wx.ALL, 5)
		return box

	def create_attachments(self):
		lbl = wx.StaticText(self, -1, _(u"Attachments"))
		self.attachments = widgetUtils.list(self, _(u"Type"), _(u"Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		return box

	def create_chat(self):
		lbl2 = wx.StaticText(self, -1, _(u"Write a message"))
		self.text = wx.TextCtrl(self, -1, size=(400, -1), style=wx.TE_MULTILINE)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl2, 0, wx.ALL, 20)
		box.Add(self.text, 0, wx.ALL, 5)
		return box

	def set_focus_function(self, focus_function):
		self.history.Bind(wx.EVT_KEY_UP , focus_function)

	def add_message(self, message, reverse=False):
		old_line = self.history.GetNumberOfLines()#.count("\n")
		point = self.history.GetInsertionPoint()
		if reverse:
			self.history.SetValue(message+"\n"+self.history.GetValue())
		else:
			self.history.AppendText(message+"\n")
		self.history.SetInsertionPoint(point)
		new_line = self.history.GetNumberOfLines()#.count("\n")
		return (old_line, new_line)

class peopleTab(homeTab):

	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Friends"))
		self.list = widgetUtils.list(self, *[_(u"Name"), _(u"Last seen")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 190)
		self.list.set_windows_size(1, 100)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.new_chat = wx.Button(self, wx.NewId(), _(u"Send message"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.new_chat, 0, wx.ALL, 5)

class videoTab(homeTab):
	def create_list(self):
		self.lbl = wx.StaticText(self, wx.NewId(), _(u"Video&s"))
		self.list = widgetUtils.list(self, *[_(u"Title"), _(u"Description"), _(u"Duration")], style=wx.LC_REPORT)
		self.list.set_windows_size(0, 160)
		self.list.set_windows_size(1, 380)
		self.list.set_windows_size(2, 80)
		self.list.set_size()
		self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

	def create_post_buttons(self):
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.play = wx.Button(self, -1, _(u"P&lay"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.play, 0, wx.ALL, 5)

class videoAlbumTab(videoTab):

	def create_post_buttons(self):
		self.load = wx.Button(self, wx.NewId(), _(u"Load album"))
		self.post = wx.Button(self, -1, _(u"&Post"))
		self.play = wx.Button(self, -1, _(u"P&lay"))
		self.postBox = wx.BoxSizer(wx.HORIZONTAL)
		self.postBox.Add(self.post, 0, wx.ALL, 5)
		self.postBox.Add(self.play, 0, wx.ALL, 5)
