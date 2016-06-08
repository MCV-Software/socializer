# -*- coding: utf-8 -*-
import wx

class postMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(postMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"Open"))
		self.AppendItem(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _(u"Like"))
		self.AppendItem(self.like)
		self.dislike = wx.MenuItem(self, wx.NewId(), _(u"Dislike"))
		self.dislike.Enable(False)
		self.AppendItem(self.dislike)
		self.comment = wx.MenuItem(self, wx.NewId(), _(u"Add comment"))
		self.AppendItem(self.comment)
		self.post_in_wall = wx.MenuItem(self, wx.NewId(), _(u"Post to this profile"))
		self.post_in_wall.Enable(False)
		self.AppendItem(self.post_in_wall)

	def create_specific_post_options(self):
		self.update = wx.MenuItem(self, wx.NewId(), _(u"Update"))
		self.AppendItem(self.update)
		self.delete = wx.MenuItem(self, wx.NewId(), _(u"Delete"))
		self.AppendItem(self.delete)

class audioMenu(wx.Menu):

	def __init__(self, *args, **kwargs):
		super(audioMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"&Open"))
		self.AppendItem(self.open)
		self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play"))
		self.AppendItem(self.play)
		self.library = wx.MenuItem(self, wx.NewId(), _(u"&Add to library"))
		self.AppendItem(self.library)

class peopleMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(peopleMenu, self).__init__(*args, **kwargs)
		self.view_profile = wx.MenuItem(self, wx.NewId(), _(u"View profile"))
		self.AppendItem(self.view_profile)
		self.message = wx.MenuItem(self, wx.NewId(), _(u"Send a message"))
		self.AppendItem(self.message)
		self.timeline = wx.MenuItem(self, wx.NewId(), _(u"Open timeline"))
		self.AppendItem(self.timeline)
		self.view_profile.Enable(False)

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
