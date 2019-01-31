# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx

class postMenu(wx.Menu):
	def __init__(self, can_delete=False, *args, **kwargs):
		super(postMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _("Open"))
		self.Append(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _("Like"))
		self.Append(self.like)
		self.dislike = wx.MenuItem(self, wx.NewId(), _("Dislike"))
		self.dislike.Enable(False)
		self.Append(self.dislike)
		self.comment = wx.MenuItem(self, wx.NewId(), _("Add comment"))
		self.Append(self.comment)
		if can_delete:
			self.delete = wx.MenuItem(self, wx.NewId(), _("Delete"))
			self.Append(self.delete)
		else:
			self.post_in_wall = wx.MenuItem(self, wx.NewId(), _("Post to this profile"))
			self.post_in_wall.Enable(False)
			self.Append(self.post_in_wall)
			self.view_profile = wx.MenuItem(self, wx.NewId(), _("View user profile"))
			self.Append(self.view_profile)

	def create_specific_post_options(self):
		self.update = wx.MenuItem(self, wx.NewId(), _("Update"))
		self.Append(self.update)
		self.delete = wx.MenuItem(self, wx.NewId(), _("Delete"))
		self.Append(self.delete)

class audioMenu(wx.Menu):

	def __init__(self, *args, **kwargs):
		super(audioMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _("&Open"))
		self.Append(self.open)
		self.play = wx.MenuItem(self, wx.NewId(), _("&Play"))
		self.Append(self.play)
		self.library = wx.MenuItem(self, wx.NewId(), _("&Add to library"))
		self.Append(self.library)
		self.move = wx.MenuItem(self, wx.NewId(), _("Move to album"))
		self.Append(self.move)

class peopleMenu(wx.Menu):
	def __init__(self, is_request=False, is_subscriber=False, *args, **kwargs):
		super(peopleMenu, self).__init__(*args, **kwargs)
		if is_request:
			self.create_request_items()
		elif is_subscriber:
			self.create_subscriber_items()
		self.view_profile = wx.MenuItem(self, wx.NewId(), _("View profile"))
		self.Append(self.view_profile)
		self.message = wx.MenuItem(self, wx.NewId(), _("Send a message"))
		self.Append(self.message)
		self.timeline = wx.MenuItem(self, wx.NewId(), _("Open timeline"))
		self.Append(self.timeline)
		self.common_friends = wx.MenuItem(self, wx.NewId(), _("View friends in common"))
		self.Append(self.common_friends)
		if is_request == False and is_subscriber == False:
			self.decline = wx.MenuItem(self, wx.NewId(), _("Remove from friends"))
			self.Append(self.decline)

	def create_request_items(self):
		self.accept = wx.MenuItem(self, wx.NewId(), _("Accept"))
		self.Append(self.accept)
		self.decline = wx.MenuItem(self, wx.NewId(), _("Decline"))
		self.Append(self.decline)
		self.keep_as_follower = wx.MenuItem(self, wx.NewId(), _("Keep as follower"))
		self.Append(self.keep_as_follower)

	def create_subscriber_items(self):
		self.add = wx.MenuItem(self, wx.NewId(), _("Add to friends"))
		self.Append(self.add)

class commentMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(commentMenu, self).__init__(*args, **kwargs)
		self.open = wx.MenuItem(self, wx.NewId(), _("Open"))
		self.Append(self.open)
		self.like = wx.MenuItem(self, wx.NewId(), _("Like"))
		self.Append(self.like)
		self.unlike = wx.MenuItem(self, -1, _("Unlike"))
		self.Append(self.unlike)

	def create_specific_comment_options(self):
		self.delete = wx.MenuItem(self, wx.NewId(), _("Delete"))
		self.Append(self.delete)

class notificationsMenu(wx.Menu):
	def __init__(self):
		super(notificationsMenu, self).__init__()
		self.mark_as_read = wx.MenuItem(self, wx.NewId(), _("Mark as read"))
		self.Append(self.mark_as_read)

class attachMenu(wx.Menu):
	def __init__(self):
		super(attachMenu, self).__init__()
		self.upload = wx.MenuItem(self, wx.NewId(), _("Upload from computer"))
		self.Append(self.upload)
		self.add = wx.MenuItem(self, wx.NewId(), _("Add from VK"))
		self.Append(self.add)

class communityBufferMenu(wx.Menu):
	def __init__(self):
		super(communityBufferMenu, self).__init__()
		load = wx.Menu()
		self.load_posts = load.Append(wx.NewId(), _("Load posts"))
		self.load_topics = load.Append(wx.NewId(), _("Load topics"))
		self.load_audios = load.Append(wx.NewId(), _("Load audios"))
		self.load_videos = load.Append(wx.NewId(), _("Load videos"))
		self.Append(wx.NewId(), _("Load"), load)