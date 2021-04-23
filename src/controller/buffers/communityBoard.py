# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
import logging
import webbrowser
import wx
import presenters
import views
import interactors
import widgetUtils
from pubsub import pub
from wxUI.tabs import communityBoard
from mysc.thread_utils import call_threaded
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.communityBoard")

class communityBoardBuffer(wallBuffer):

	def create_tab(self, parent):
		self.tab = communityBoard.communityBoardTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if "can_create_topic" not in self.session.db["group_info"][self.kwargs["group_id"]*-1] or ("can_create_topic" in self.session.db["group_info"][self.kwargs["group_id"]*-1] and self.session.db["group_info"][self.kwargs["group_id"]*-1]["can_create_topic"] != True):
			self.tab.post.Enable(False)

	def onFocus(self, event, *args, **kwargs):
		event.Skip()

	def open_post(self, *args, **kwargs):
		""" Opens the currently focused post."""
		post = self.get_post()
		if post == None:
			return
		a = presenters.displayTopicPresenter(session=self.session, postObject=post, group_id=self.kwargs["group_id"], interactor=interactors.displayPostInteractor(), view=views.displayTopic())

	def open_in_browser(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		# In order to load the selected topic we firstly have to catch the group_id, which is present in self.kwargs
		# After getting the group_id we should make it negative
		group_id = self.kwargs["group_id"]*-1
		url = "https://vk.com/topic{group_id}_{topic_id}".format(group_id=group_id, topic_id=post["id"])
		webbrowser.open_new_tab(url)

	def post(self, *args, **kwargs):
		menu = wx.Menu()
		user1 = self.session.get_user(self.session.user_id)
		user2 = self.session.get_user(-1*self.kwargs["group_id"])
		user = menu.Append(wx.NewId(), _("Post as {user1_nom}").format(**user1))
		group = menu.Append(wx.NewId(), _("Post as {user1_nom}").format(**user2))
		menu.Bind(widgetUtils.MENU, lambda evt: self._post(evt, 1), group)
		menu.Bind(widgetUtils.MENU, lambda evt: self._post(evt, 0), user)
		self.tab.post.PopupMenu(menu, self.tab.post.GetPosition())

	def _post(self, event, from_group):
		owner_id = self.kwargs["group_id"]
		user = self.session.get_user(-1*owner_id, key="user1")
		title = _("Create topic in {user1_nom}").format(**user)
		p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createTopicDialog(title=title, message="", text="", topic_title=""))
		if hasattr(p, "text") or hasattr(p, "privacy"):
			title = p.view.title.GetValue()
			msg = p.text
			post_arguments = dict(title=title, text=msg, group_id=owner_id, from_group=from_group)
			attachments = []
			if hasattr(p, "attachments"):
				attachments = p.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="board", child_endpoint="addTopic", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)