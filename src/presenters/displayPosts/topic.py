# -*- coding: utf-8 -*-
import threading
import arrow
import languageHandler
import views
import interactors
import output
import logging
from pubsub import pub
from sessionmanager import utils # We'll use some functions from there
from mysc.thread_utils import call_threaded
from presenters import base
from presenters.createPosts.basePost import createPostPresenter
from . import basePost
from .topicComment import *

log = logging.getLogger(__file__)

class displayTopicPresenter(basePost.displayPostPresenter):

	def __init__(self, session, postObject, group_id, view, interactor):
		self.type = "topic"
		self.modulename = "display_topic"
		self.interactor = interactor
		self.view = view
		self.interactor.install(view=view, presenter=self, modulename=self.modulename)
		self.session = session
		self.post = postObject
		self.group_id = group_id
		self.load_images = False
		# We'll put images here, so it will be easier to work with them.
		self.images = []
		self.imageIndex = 0
		result = self.get_post_information()
		# Stop loading everything else if post was deleted.
		if result == False:
			self.interactor.uninstall()
			return
		self.worker = threading.Thread(target=self.load_all_components)
		self.worker.finished = threading.Event()
		self.worker.start()
		self.attachments = []
		# connect pubsub event for posted comments.
		pub.subscribe(self.posted, "posted")
		self.run()
		pub.unsubscribe(self.posted, "posted")

	def load_all_components(self):
		self.get_comments()

	def get_post_information(self):
		title = self.post["title"]
		self.send_message("set_title", value=title)
		return True

	def get_comments(self):
		""" Get comments and insert them in a list."""
		self.comments = self.session.vk.client.board.getComments(group_id=self.group_id, topic_id=self.post["id"], need_likes=1, count=100, extended=1, sort="desc")
		comments_ = []
		data = dict(profiles=self.comments["profiles"], groups=[])
		self.session.process_usernames(data)
		self.comments["items"].reverse()
		# If there are less than 100 comments in the topic we should disable the "load previous" button.
		if self.comments["count"] <= 100:
			self.send_message("disable_control", control="load_more_comments")
		else:
			left_comments = self.comments["count"]-len(self.comments["items"])
			if left_comments > 100:
				left_comments = 100
			self.send_message("set_label", control="load_more_comments", label=_("Load {comments} previous comments").format(comments=left_comments))
		for i in self.comments["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = self.session.get_user(i["from_id"])["user1_nom"]
			# match user mentions inside text comment.
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(i["likes"]["count"])
			text = utils.clean_text(text=i["text"])
			comments_.append((from_, text, created_at, likes))
		self.send_message("add_items", control="comments", items=comments_)

	def post_like(self):
		c = self.interactor.view.comments.get_selected()
		id = self.comments["items"][c]["id"]
		if self.comments["items"][c]["likes"]["user_likes"] == 1:
			l = self.session.vk.client.likes.delete(owner_id=-1*self.group_id, item_id=id, type="topic_comment")
			output.speak(_("You don't like this"))
			self.comments["items"][c]["likes"]["count"] = l["likes"]
			self.comments["items"][c]["likes"]["user_likes"] = 2
			self.send_message("set_label", control="like", label=_("&Like"))
		else:
			l = self.session.vk.client.likes.add(owner_id=-1*self.group_id, item_id=id, type="topic_comment")
			output.speak(_("You liked this"))
			self.send_message("set_label", control="like", label=_("&Dislike"))
			self.comments["items"][c]["likes"]["count"] = l["likes"]
			self.comments["items"][c]["likes"]["user_likes"] = 1
		self.clear_comments_list()

	def change_comment(self, comment):
		comment = self.comments["items"][comment]
		self.send_message("clean_list", list="attachments")
		self.get_attachments(comment, "")
		if comment["likes"]["user_likes"] == 1:
			self.send_message("set_label", control="like", label=_("&Dislike"))
		else:
			self.send_message("set_label", control="like", label=_("&Like"))

	def add_comment(self):
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Add a comment"), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			post_arguments = dict(group_id=self.group_id, topic_id=self.post["id"], message=comment.text)
			attachments = []
			if hasattr(comment, "attachments"):
				attachments = comment.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="board", child_endpoint="createComment", attachments_list=attachments, post_arguments=post_arguments)

	def reply(self, comment):
		c = self.comments["items"][comment]
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {user1_nom}").format(**self.session.get_user(c["from_id"])), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			user = self.session.get_user(c["from_id"])
			name = user["user1_nom"].split(" ")[0]
			comment.text = "[post{post_id}|{name}], {text}".format(post_id=c["id"], text=comment.text, name=name)
			group_id = self.group_id
			topic_id = self.post["id"]
			post_arguments = dict(group_id=group_id, topic_id=topic_id, reply_to_comment=c["id"], message=comment.text)
			attachments = []
			if hasattr(comment, "attachments"):
				attachments = comment.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="board", child_endpoint="createComment", attachments_list=attachments, post_arguments=post_arguments)

	def show_comment(self, comment_index):
		c = self.comments["items"][comment_index]
		c["post_id"] = self.post["id"]
		c["group_id"] = -1*self.group_id
		a = displayTopicCommentPresenter(session=self.session, postObject=c, interactor=interactors.displayPostInteractor(), view=views.displayComment())

	def load_more_comments(self):
		offset = len(self.comments["items"])
		comments = self.session.vk.client.board.getComments(group_id=self.group_id, topic_id=self.post["id"], need_likes=1, count=100, extended=1, sort="desc", offset=offset)
		data = dict(profiles=comments["profiles"], groups=[])
		self.session.process_usernames(data)
		# If there are less than 100 comments in the topic we should disable the "load previous" button.
		for i in comments["items"]:
			self.comments["items"].insert(0, i)
		for i in comments["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = self.session.get_user(i["from_id"])["user1_nom"]
			# match user mentions inside text comment.
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(i["likes"]["count"])
			text = utils.clean_text(text=i["text"])
			self.send_message("add_item", control="comments", item=(from_, text, created_at, likes), reversed=True)
		if len(self.comments["items"]) == self.comments["count"]:
			self.send_message("disable_control", control="load_more_comments")
		else:
			left_comments = self.comments["count"]-len(self.comments["items"])
			if left_comments > 100:
				left_comments = 100
			self.send_message("set_label", control="load_more_comments", label=_("Load {comments} previous comments").format(comments=left_comments))

	def posted(self, from_buffer=None):
		self.clear_comments_list()