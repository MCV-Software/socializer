# -*- coding: utf-8 -*-
import logging
import output
from pubsub import pub
from sessionmanager import renderers, utils # We'll use some functions from there
from presenters import base
from presenters.createPosts.basePost import createPostPresenter
from . import comment

log = logging.getLogger(__file__)

def get_message(status):
	message = ""
	if "text" in status:
		message = utils.clean_text(status["text"])
	return message

class displayTopicCommentPresenter(comment.displayCommentPresenter):

	def get_post_information(self):
		from_ = self.session.get_user(self.post[self.user_identifier])
		title = from_["user1_nom"]
		self.send_message("set_title", value=title)
		message = ""
		message = get_message(self.post)
		self.send_message("set", control="post_view", value=message)
		self.get_attachments(self.post, message)
		self.check_image_load()
		self.send_message("disable_control", control="reply")
		self.send_message("disable_control", control="comments")

	def post_like(self):
		id = self.post["id"]
		if self.post["likes"]["user_likes"] == 1:
			l = self.session.vk.client.likes.delete(owner_id=self.post["group_id"], item_id=id, type="topic_comment")
			output.speak(_("You don't like this"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 2
			self.send_message("set_label", control="like", label=_("&Like"))
		else:
			l = self.session.vk.client.likes.add(owner_id=self.post["group_id"], item_id=id, type="topic_comment")
			output.speak(_("You liked this"))
			self.send_message("set_label", control="like", label=_("&Dislike"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 1
		self.get_likes()

	def show_likes(self):
		""" show likes for the specified post."""
		data = dict(type="topic_comment", owner_id=self.post["group_id"], item_id=self.post["id"], extended=True, count=100, skip_own=True)
		result = self.session.vk.client.likes.getList(**data)
		if result["count"] > 0:
			post = {"source_id": self.post["group_id"], "friends": {"items": result["items"]}}
			pub.sendMessage("open-post", post_object=post, controller_="displayFriendship", vars=dict(caption=_("people who liked this")))