# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
import logging
import wx
import presenters
import views
import interactors
import widgetUtils
import output
from pubsub import pub
from wxUI.tabs import communityWall
from mysc.thread_utils import call_threaded
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.communityWall")

class communityWallBuffer(wallBuffer):

	def __init__(self, *args, **kwargs):
		super(communityWallBuffer, self).__init__(*args, **kwargs)
		self.group_id = self.kwargs["owner_id"]

	def create_tab(self, parent):
		self.tab = communityWall.communityWallTab(parent)
		self.connect_events()
		self.tab.name = self.name
		self.tab.post.Enable(False)

	def connect_events(self):
		super(communityWallBuffer, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_community)

	def load_community(self, *args, **kwargs):
		output.speak(_("Loading community..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)

	def get_items(self, *args, **kwargs):
		""" This method retrieves community information, useful to show different parts of the community itself."""
		if self.can_get_items:
			# Strangely, groups.get does not return counters so we need those to show options for loading specific posts for communities.
			group_info = self.session.vk.client.groups.getById(group_ids=-1*self.kwargs["owner_id"], fields="counters")[0]
			self.session.db["group_info"][self.group_id].update(group_info)
			if "can_post" in self.session.db["group_info"][self.group_id] and self.session.db["group_info"][self.group_id]["can_post"] == True:
				self.tab.post.Enable(True)
		super(communityWallBuffer, self).get_items(*args, **kwargs)

	def post(self, *args, **kwargs):
		menu = wx.Menu()
		user1 = self.session.get_user(self.session.user_id)
		user2 = self.session.get_user(self.kwargs["owner_id"])
		user = menu.Append(wx.NewId(), _("Post as {user1_nom}").format(**user1))
		group = menu.Append(wx.NewId(), _("Post as {user1_nom}").format(**user2))
		menu.Bind(widgetUtils.MENU, lambda evt: self._post(evt, 1), group)
		menu.Bind(widgetUtils.MENU, lambda evt: self._post(evt, 0), user)
		self.tab.post.PopupMenu(menu, self.tab.post.GetPosition())

	def _post(self, event, from_group):
		owner_id = self.kwargs["owner_id"]
		user = self.session.get_user(owner_id, key="user1")
		title = _("Post to {user1_nom}'s wall").format(**user)
		p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=title, message="", text=""))
		if hasattr(p, "text") or hasattr(p, "privacy"):
			post_arguments=dict(privacy=p.privacy, message=p.text, owner_id=owner_id, from_group=from_group)
			attachments = []
			if hasattr(p, "attachments"):
				attachments = p.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="post", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)