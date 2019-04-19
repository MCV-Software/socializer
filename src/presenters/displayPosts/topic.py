# -*- coding: utf-8 -*-
import threading
import arrow
import languageHandler
import views
import interactors
import output
import logging
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
		self.run()

	def load_all_components(self):
		self.get_comments()

	def get_post_information(self):
		title = self.post["title"]
		self.send_message("set_title", value=title)
		return True

	def get_comments(self):
		""" Get comments and insert them in a list."""
		self.comments = self.session.vk.client.board.getComments(group_id=self.group_id, topic_id=self.post["id"], need_likes=1, count=100, extended=1)
		comments_ = []
		data = dict(profiles=self.comments["profiles"], groups=[])
		self.session.process_usernames(data)
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
			group_id = self.group_id
			topic_id = self.post["id"]
			call_threaded(self.do_last, comment, group_id=group_id, topic_id=topic_id)

	def do_last(self, comment, **kwargs):
		msg = comment.text
		attachments = ""
		if hasattr(comment, "attachments"):
			attachments = self.upload_attachments(comment.attachments)
		urls = utils.find_urls_in_text(msg)
		if len(urls) != 0:
			if len(attachments) == 0: attachments = urls[0]
			else: attachments += urls[0]
			msg = msg.replace(urls[0], "")
		if msg != "":
			kwargs.update(message=msg)
		if attachments != "":
			kwargs.update(attachments=attachments)
		if "message" not in kwargs and "attachments" not in kwargs:
			return # No comment made here.
		result = self.session.vk.client.board.createComment(**kwargs)
		self.clear_comments_list()

	def reply(self, comment):
		c = self.comments["items"][comment]
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {user1_nom}").format(**self.session.get_user(c["from_id"])), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			user = self.session.get_user(c["from_id"])
			name = user["user1_nom"].split(" ")[0]
			comment.text = "[post{post_id}|{name}], {text}".format(post_id=c["id"], text=comment.text, name=name)
			group_id = self.group_id
			topic_id = self.post["id"]
			call_threaded(self.do_last, comment, group_id=group_id, topic_id=topic_id, reply_to_comment=c["id"])

	def show_comment(self, comment_index):
		c = self.comments["items"][comment_index]
		c["post_id"] = self.post["id"]
		a = displayTopicCommentPresenter(session=self.session, postObject=c, interactor=interactors.displayPostInteractor(), view=views.displayComment())