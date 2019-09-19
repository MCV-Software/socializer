# -*- coding: utf-8 -*-
import threading
import arrow
import languageHandler
import views
import interactors
import logging
from pubsub import pub
from sessionmanager import renderers, utils # We'll use some functions from there
from mysc.thread_utils import call_threaded
from presenters import base
from presenters.createPosts.basePost import createPostPresenter
from . import basePost

log = logging.getLogger(__file__)

def get_message(status):
	message = ""
	if "text" in status:
		message = utils.clean_text(status["text"])
	return message

class displayCommentPresenter(basePost.displayPostPresenter):

	def __init__(self, session, postObject, view, interactor):
		self.type = "comment"
		self.modulename = "display_comment"
		self.interactor = interactor
		self.view = view
		self.interactor.install(view=view, presenter=self, modulename=self.modulename)
		self.session = session
		self.post = postObject
		self.user_identifier = "from_id"
		self.post_identifier = "id"
		self.worker = threading.Thread(target=self.load_all_components)
		self.worker.finished = threading.Event()
		self.worker.start()
		self.attachments = []
		self.load_images = False
		# We'll put images here, so it will be easier to work with them.
		self.images = []
		self.imageIndex = 0
		# connect here the pubsub event for successful posting of comments.
		pub.subscribe(self.posted, "posted")
		self.run()
		pub.unsubscribe(self.posted, "posted")

	def load_all_components(self):
		self.get_post_information()
		self.get_likes()
		self.send_message("disable_control", control="comment")
		if self.post["likes"]["can_like"] == 0 and self.post["likes"]["user_likes"] == 0:
			self.send_message("disable_control", "like")
		elif self.post["likes"]["user_likes"] == 1:
			self.send_message("set_label", control="like", label=_("&Dislike"))

	def get_post_information(self):
		from_ = self.session.get_user(self.post[self.user_identifier])
		if ("from_id" in self.post and "owner_id" in self.post):
			user2 = self.session.get_user(self.post["owner_id"], "user2")
			user2.update(from_)
			title = _("Comment from {user1_nom} in the {user2_nom}'s post").format(**user2)
		self.send_message("set_title", value=title)
		message = ""
		message = get_message(self.post)
		self.send_message("set", control="post_view", value=message)
		self.get_attachments(self.post, message)
		self.check_image_load()

	def reply(self, *args, **kwargs):
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {user1_nom}").format(**self.session.get_user(self.post["from_id"])), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			post_arguments = dict(owner_id=self.post["owner_id"], reply_to_comment=self.post["id"], post_id=self.post["post_id"], reply_to_user=self.post["owner_id"], message=comment.text)
			attachments = []
			if hasattr(comment, "attachments"):
				attachments = comment.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="createComment", attachments_list=attachments, post_arguments=post_arguments)

	def show_likes(self):
		""" show likes for the specified post."""
		data = dict(type="comment", owner_id=self.post["owner_id"], item_id=self.post["id"], extended=True, count=100, skip_own=True)
		result = self.session.vk.client.likes.getList(**data)
		if result["count"] > 0:
			post = {"source_id": self.post[self.user_identifier], "friends": {"items": result["items"]}}
			pub.sendMessage("open-post", post_object=post, controller_="displayFriendship", vars=dict(caption=_("people who liked this")))

	def posted(self, from_buffer=None):
		self.interactor.uninstall()
		return