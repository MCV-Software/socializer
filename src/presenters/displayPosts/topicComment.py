# -*- coding: utf-8 -*-
import logging
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