# -*- coding: utf-8 -*-
""" This module contains all context menus needed to be displayed in different sections. Basically any menu that is bigger than 2 menu items should be here."""
from __future__ import unicode_literals
import wx

class postMenu(wx.Menu):
	""" Display a menu with actions related to posts in the news feed or walls. """

	def __init__(self, can_delete=False, *args, **kwargs):
		super(postMenu, self).__init__(*args, **kwargs)
		self.open = self.Append(wx.NewId(), _("Open"))
		self.like = self.Append(wx.NewId(), _("Like"))
		self.dislike = self.Append(wx.NewId(), _("Dislike"))
		self.dislike.Enable(False)
		self.comment = self.Append(wx.NewId(), _("Add comment"))
		if can_delete:
			self.delete = self.Append(wx.NewId(), _("Delete"))
		else:
			self.post_in_wall = self.Append(wx.NewId(), _("Post to this profile"))
			self.post_in_wall.Enable(False)
			self.view_profile = self.Append(wx.NewId(), _("View user profile"))
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

class audioMenu(wx.Menu):

	def __init__(self, *args, **kwargs):
		super(audioMenu, self).__init__(*args, **kwargs)
		self.open = self.Append(wx.NewId(), _("&Open"))
		self.play = self.Append(wx.NewId(), _("&Play"))
		self.library = self.Append(wx.NewId(), _("&Add to library"))
		self.move = self.Append(wx.NewId(), _("Move to album"))
#		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

class peopleMenu(wx.Menu):
	def __init__(self, is_request=False, is_subscriber=False, not_friend=False, *args, **kwargs):
		super(peopleMenu, self).__init__(*args, **kwargs)
		if is_request:
			self.create_request_items()
		elif is_subscriber:
			self.create_subscriber_items()
		self.view_profile = self.Append(wx.NewId(), _("View profile"))
		self.message = self.Append(wx.NewId(), _("Send a message"))
		self.timeline = self.Append(wx.NewId(), _("Open timeline"))
		if not_friend == False:
			self.common_friends = self.Append(wx.NewId(), _("View friends in common"))
		if is_request == False and is_subscriber == False and not_friend == False:
			self.decline = self.Append(wx.NewId(), _("Remove from friends"))
		self.block = self.Append(wx.NewId(), _("Block"))
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

	def create_request_items(self):
		self.accept = self.Append(wx.NewId(), _("Accept"))
		self.decline = self.Append(wx.NewId(), _("Decline"))
		self.keep_as_follower = self.Append(wx.NewId(), _("Keep as follower"))
		self.block = self.Append(wx.NewId(), _("Block"))

	def create_subscriber_items(self):
		self.add = self.Append(wx.NewId(), _("Add to friends"))
		self.block = self.Append(wx.NewId(), _("Block"))

class documentMenu(wx.Menu):
	def __init__(self, added=False, *args, **kwargs):
		super(documentMenu, self).__init__(*args, **kwargs)
		self.download = self.Append(wx.NewId(), _("Download document"))
		if added == True:
			self.action = self.Append(wx.NewId(), _("Remove from my documents"))
		else:
			self.action = self.Append(wx.NewId(), _("Add to my documents"))
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

class commentMenu(wx.Menu):
	def __init__(self, *args, **kwargs):
		super(commentMenu, self).__init__(*args, **kwargs)
		self.open = self.Append(wx.NewId(), _("Open"))
		self.like = self.Append(wx.NewId(), _("Like"))
		self.dislike = self.Append(wx.NewId(), _("Dislike"))
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

class attachMenu(wx.Menu):
	def __init__(self):
		super(attachMenu, self).__init__()
		self.upload = self.Append(wx.NewId(), _("Upload from computer"))
		self.add = self.Append(wx.NewId(), _("Add from VK"))

class communityBufferMenu(wx.Menu):
	def __init__(self):
		super(communityBufferMenu, self).__init__()
		load = wx.Menu()
		self.load_posts = load.Append(wx.NewId(), _("Load posts"))
		self.load_topics = load.Append(wx.NewId(), _("Load topics"))
		self.load_audios = load.Append(wx.NewId(), _("Load audios"))
		self.load_videos = load.Append(wx.NewId(), _("Load videos"))
		self.load_documents = load.Append(wx.NewId(), _("Load documents"))
		self.Append(wx.NewId(), _("Load"), load)
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))

class conversationBufferMenu(wx.Menu):
	def __init__(self):
		super(conversationBufferMenu, self).__init__()
		self.delete = self.Append(wx.NewId(), _("Delete conversation"))
		self.open_in_browser = self.Append(wx.NewId(), _("Open in vk.com"))