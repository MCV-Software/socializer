# -*- coding: utf-8 -*-
import wx

class postMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(postMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"Open"))
		self.Append(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _(u"Like"))
		self.Append(self.like)
		self.dislike = wx.MenuItem(self, wx.NewId(), _(u"Dislike"))
		self.dislike.Enable(False)
		self.Append(self.dislike)
		self.comment = wx.MenuItem(self, wx.NewId(), _(u"Add comment"))
		self.Append(self.comment)
		self.post_in_wall = wx.MenuItem(self, wx.NewId(), _(u"Post to this profile"))
		self.post_in_wall.Enable(False)
		self.Append(self.post_in_wall)
		self.view_profile = wx.MenuItem(self, wx.NewId(), _(u"View user profile"))
		self.Append(self.view_profile)

	def create_specific_post_options(self):
		self.update = wx.MenuItem(self, wx.NewId(), _(u"Update"))
		self.Append(self.update)
		self.delete = wx.MenuItem(self, wx.NewId(), _(u"Delete"))
		self.Append(self.delete)

class audioMenu(wx.Menu):

	def __init__(self, *args, **kwargs):
		super(audioMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"&Open"))
		self.Append(self.open)
		self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play"))
		self.Append(self.play)
		self.library = wx.MenuItem(self, wx.NewId(), _(u"&Add to library"))
		self.Append(self.library)
		self.move = wx.MenuItem(self, wx.NewId(), _(u"Move to album"))
		self.Append(self.move)

class peopleMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(peopleMenu, self).__init__(*args, **kwargs)
		self.view_profile = wx.MenuItem(self, wx.NewId(), _(u"View profile"))
		self.Append(self.view_profile)
		self.message = wx.MenuItem(self, wx.NewId(), _(u"Send a message"))
		self.Append(self.message)
		self.timeline = wx.MenuItem(self, wx.NewId(), _(u"Open timeline"))
		self.Append(self.timeline)

class commentMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(commentMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _(u"Open"))
		self.Append(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _(u"Like"))
		self.Append(self.like)
		self.unlike = wx.MenuItem(self, -1, _(u"Unlike"))
		self.Append(self.unlike)

	def create_specific_comment_options(self):
		self.delete = wx.MenuItem(self, wx.NewId(), _(u"Delete"))
		self.Append(self.delete)

class notificationsMenu(wx.Menu):
	def __init__(self):
		super(notificationsMenu, self).__init__()
		self.mark_as_read = wx.MenuItem(self, wx.NewId(), _(u"Mark as read"))
		self.Append(self.mark_as_read)
