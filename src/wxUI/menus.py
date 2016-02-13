# -*- coding: utf-8 -*-
import wx

class postMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(postMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"Open"))
		self.AppendItem(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _(u"Like"))
		self.AppendItem(self.like)
		self.unlike = wx.MenuItem(self, wx.NewId(), _(u"Unlike"))
		self.AppendItem(self.unlike)
		self.comment = wx.MenuItem(self, wx.NewId(), _(u"Add comment"))
		self.AppendItem(self.comment)
		self.post_in_wall = self.Append(wx.NewId(), _(u"Post to this profile"))
		self.AppendItem(self.post_in_wall)
		self.post_in_wall.Enable(False)

	def create_specific_post_options(self):
		self.update = wx.MenuItem(self, wx.NewId(), _(u"Update"))
		self.AppendItem(self.update)
		self.delete = wx.MenuItem(self, wx.NewId(), _(u"Delete"))
		self.AppendItem(self.delete)

class commentMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(commentMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"Open"))
		self.AppendItem(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _(u"Like"))
		self.AppendItem(self.like)
		self.unlike = wx.MenuItem(self, -1, _(u"Unlike"))
		self.AppendItem(self.unlike)

	def create_specific_comment_options(self):
		self.delete = wx.MenuItem(self, wx.NewId(), _(u"Delete"))
		self.AppendItem(self.delete)

class notificationsMenu(wx.Menu):
	def __init__(self):
		super(notificationsMenu, self).__init__()
		self.mark_as_read = wx.MenuItem(self, wx.NewId(), _(u"Mark as read"))
		self.AppendItem(self.mark_as_read)

class toolsMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(toolsMenu, self).__init__(*args, **kwargs)
		self.url = wx.MenuItem(self, -1, _(u"Open URL"))
		self.AppendItem(self.url)
#		self.url.Enable(False)
		self.translate = wx.MenuItem(self, -1, _(u"Translate"))
		self.AppendItem(self.translate)
		self.CheckSpelling = wx.MenuItem(self, -1, _(u"Check Spelling"))
		self.AppendItem(self.CheckSpelling)
