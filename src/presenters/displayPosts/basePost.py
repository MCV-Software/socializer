# -*- coding: utf-8 -*-
import threading
import arrow
import requests
import languageHandler
import views
import interactors
import output
import webbrowser
import logging
from vk_api import upload
from sessionmanager import session, renderers, utils # We'll use some functions from there
from pubsub import pub
from extra import SpellChecker, translator
from mysc.thread_utils import call_threaded
from presenters import base
from presenters.createPosts.basePost import createPostPresenter
from . import audio, poll, article

log = logging.getLogger(__file__)

def get_message(status):
	message = ""
	if "text" in status:
		message = utils.clean_text(status["text"])
	return message

class displayPostPresenter(base.basePresenter):
	""" Base class for post representation."""

	def __init__(self, session, postObject, view, interactor):
		super(displayPostPresenter, self).__init__(view=view, interactor=interactor, modulename="display_post")
		self.type = "post"
		self.session = session
		self.post = postObject
		# Posts from newsfeed contains this source_id instead from_id in walls. Also it uses post_id and walls use just id.
		if "source_id" in self.post:
			self.user_identifier = "source_id"
			self.post_identifier = "post_id"
		else:
			# In wall's posts, if someone has posted in user's wall, owner_id should be used instead from_id
			# This will help for retrieving comments, do likes, etc.
			if "owner_id" not in self.post:
				self.user_identifier = "from_id"
			else:
				self.user_identifier = "owner_id"
			self.post_identifier = "id"
		self.attachments = []
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
		# connect here the pubsub event for successful posting of comments.
		pub.subscribe(self.posted, "posted")
		self.run()
		pub.unsubscribe(self.posted, "posted")

	def posted(self, from_buffer=None):
		self.clear_comments_list()

	def get_comments(self):
		""" Get comments and insert them in a list."""
		user = self.post[self.user_identifier]
		id = self.post[self.post_identifier]
		comments_data = self.session.vk.client.wall.getComments(owner_id=user, post_id=id, need_likes=1, count=100, extended=1, preview_length=0, thread_items_count=10)
		self.comments = dict(items=[], profiles=comments_data["profiles"])
		for i in comments_data["items"]:
			self.comments["items"].append(i)
			if i.get("thread") != None and i["thread"].get("count") > 0:
				for newI in i["thread"]["items"]:
					self.comments["items"].append(newI)
		comments_ = []
		# Save profiles in session local storage for a future usage.
		# Although community objects are returned here, we should not add those because their names are changed.
		# For example, self reference to a group is marked as "Administrator", which would ruin this profile to be rendered somewhere else.
		data = dict(groups=[], profiles=self.comments["profiles"])
		self.session.process_usernames(data)
		for i in self.comments["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = self.session.get_user(i["from_id"])["user1_nom"]
			if "reply_to_user" in i:
				extra_info = self.session.get_user(i["reply_to_user"])["user1_nom"]
				from_ = _("{0} > {1}").format(from_, extra_info)
			# As we set the comment reply properly in the from_ field, let's remove the first username from here if it exists.
			fixed_text = utils.clean_text(i["text"])
			if len(fixed_text) > 140:
				text = fixed_text[:141]
			else:
				text = fixed_text
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(i["likes"]["count"])
			comments_.append((from_, text, created_at, likes))
		self.send_message("add_items", control="comments", items=comments_)

	def get_post_information(self):
		from_ = self.session.get_user(self.post[self.user_identifier])
		if "copy_history" in self.post:
			title = _("repost from {user1_nom}").format(**from_)
		else:
			if ("from_id" in self.post and "owner_id" in self.post) and (self.post["from_id"] != self.post["owner_id"]):
				# Translators: {0} will be replaced with the user who is posting, and {1} with the wall owner.
				user2 = self.session.get_user(self.post["owner_id"], "user2")
				user2.update(from_)
				title = _("Post from {user1_nom} in the {user2_nom}'s wall").format(**user2)
			else:
				title = _("Post from {user1_nom}").format(**from_)
		self.send_message("set_title", value=title)
		message = ""
		# Retrieve again the post, so we'll make sure to get the most up to date information.
		# And we add a counter for views.
		post = self.session.vk.client.wall.getById(posts="{owner_id}_{post_id}".format(owner_id=self.post[self.user_identifier], post_id=self.post[self.post_identifier]))
		# If this post has been deleted, let's send an event to the interactor so it won't be displayed.
		if len(post) == 0:
			self.send_message("post_deleted")
			return False
		self.post = post[0]
		if "views" in self.post and self.post["views"]["count"] > 0:
			self.send_message("set", control="views", value=str(self.post["views"]["count"]))
		else:
			self.send_message("disable_control", control="views")
		if "owner_id" not in self.post:
			self.user_identifier = "from_id"
		else:
			self.user_identifier = "owner_id"
		self.post_identifier = "id"
		message = get_message(self.post)
		if "copy_history" in self.post:
			nm = "\n"
			for i in self.post["copy_history"]:
				u = self.session.get_user(i["from_id"])
				u.update(message=get_message(i))
				nm += "{user1_nom}: {message}\n\n".format(**u)
				self.get_attachments(i, get_message(i))
			message += nm
		self.send_message("set", control="post_view", value=message)
		self.get_attachments(self.post, message)
		self.check_image_load()

	def get_attachments(self, post, text):
		attachments = []
		self.attachments = []
		if "attachments" in post:
			for i in post["attachments"]:
				# We don't need the photos_list attachment, so skip it.
				if i["type"] == "photos_list":
					continue
				if i["type"] == "photo":
					if self.load_images == False: self.load_images = True
					self.images.append(i)
				attachments.append(renderers.add_attachment(i))
				self.attachments.append(i)
		# Links in text are not treated like normal attachments, so we'll have to catch and add those to the list without title
		# We can't get a title because title is provided by the VK API and it will not work for links as simple text.
		urls = utils.find_urls_in_text(text)
		if len(urls) > 0:
			links = []
			for i in urls:
				links.append({"link": {"title": _("Untitled link"), "url": i}, "type": "link"})
			for i in links:
				attachments.append(renderers.add_attachment(i))
				self.attachments.append(i)
		if len(self.attachments) > 0:
			self.send_message("enable_attachments")
			self.send_message("add_items", control="attachments", items=attachments)
		else:
			self.interactor.view.attachments.list.Enable(False)

	def check_image_load(self):
		if self.load_images and len(self.images) > 0 and self.session.settings["general"]["load_images"]:
			self.send_message("enable_control", control="image")
			nav = False # Disable navigation controls in photos
			if len(self.images) > 1:
				nav = True
			self.send_message("enable_photo_controls", navigation=nav)
			self.set_image(0)

	def set_next_image(self, *args, **kwargs):
		if self.imageIndex < -1 or self.imageIndex == len(self.images)-1:
			self.imageIndex = -1
		if len(self.images) <= self.imageIndex+1:
			self.imageIndex = 0
		else:
			self.imageIndex = self.imageIndex + 1
		self.set_image(self.imageIndex)

	def set_previous_image(self, *args, **kwargs):
		if self.imageIndex <= 0:
			self.imageIndex = len(self.images)
		self.imageIndex = self.imageIndex - 1
		self.set_image(self.imageIndex)

	def set_image(self, index):
		if len(self.images) < index-1:
			return
		# Get's photo URL.
		url = self.get_photo_url(self.images[index]["photo"], "x")
		if url != "":
			img = requests.get(url)
			self.send_message("load_image", image=img)
			# Translators: {0} is the number of the current photo and {1} is the total number of photos.
			output.speak(_("Loaded photo {0} of {1}").format(index+1, len(self.images)))
		return

	def get_photo_url(self, photo, size="x"):
		url = ""
		for i in photo["sizes"]:
			if i["type"] == size:
				url = i["url"]
				break
		return url

	def load_all_components(self):
		self.get_likes()
		self.get_reposts()
		self.get_comments()
		if self.post["comments"]["can_post"] == 0:
			self.send_message("disable_control", control="comment")
		if self.post["likes"]["can_like"] == 0 and self.post["likes"]["user_likes"] == 0:
			self.send_message("disable_control", "like")
		elif self.post["likes"]["user_likes"] == 1:
			self.send_message("set_label", control="like", label=_("&Dislike"))
		if self.post["likes"]["can_publish"] == 0:
			self.send_message("disable_control", control="repost")

	def post_like(self):
		if ("owner_id" in self.post) == False:
			user = int(self.post[self.user_identifier])
		else:
			user = int(self.post["owner_id"])
		id = int(self.post[self.post_identifier])
		if "type" in self.post:
			type_ = self.post["type"]
		else:
			type_ = self.type
		if self.post["likes"]["user_likes"] == 1:
			l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
			output.speak(_("You don't like this"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 2
			self.get_likes()
			self.send_message("set_label", control="like", label=_("&Like"))
		else:
			l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
			output.speak(_("You liked this"))
			self.send_message("set_label", control="like", label=_("&Dislike"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 1
			self.get_likes()

	def post_repost(self):
		object_id = "wall{0}_{1}".format(self.post[self.user_identifier], self.post[self.post_identifier])
		p = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Repost"), message=_("Add your comment here"), text="", mode="comment"))
		if hasattr(p, "text") or hasattr(p, "privacy"):
			post_arguments = dict(object=object_id, message=p.text)
			attachments = []
			if hasattr(p, "attachments"):
				attachments = p.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="repost", attachments_list=attachments, post_arguments=post_arguments)

	def get_likes(self):
		self.send_message("set_label", control="likes", label=_("{0} people like this").format(self.post["likes"]["count"],))

	def get_reposts(self):
		self.send_message("set_label", control="shares", label=_("Shared {0} times").format(self.post["reposts"]["count"],))

	def add_comment(self):
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Add a comment"), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			owner_id = self.post[self.user_identifier]
			post_id = self.post[self.post_identifier]
			post_arguments=dict(message=comment.text, owner_id=owner_id, post_id=post_id)
			attachments = []
			if hasattr(comment, "attachments"):
				attachments = comment.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="createComment", attachments_list=attachments, post_arguments=post_arguments)

	def reply(self, comment):
		c = self.comments["items"][comment]
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {user1_nom}").format(**self.session.get_user(c["from_id"])), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			post_id = self.post[self.post_identifier]
			post_arguments=dict(message=comment.text, owner_id=c["owner_id"], reply_to_comment=c["id"], post_id=c["post_id"], reply_to_user=c["owner_id"])
			attachments = []
			if hasattr(comment, "attachments"):
				attachments = comment.attachments
			call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="createComment", attachments_list=attachments, post_arguments=post_arguments)

	def show_comment(self, comment_index):
		from . import comment
		c = self.comments["items"][comment_index]
		c["post_id"] = self.post[self.post_identifier]
		a = comment.displayCommentPresenter(session=self.session, postObject=c, interactor=interactors.displayPostInteractor(), view=views.displayComment())

	def translate(self, text, language):
		msg = translator.translator.translate(text, language)
		self.send_message("set", control="post_view", value=msg)
		self.send_message("focus_control", control="post_view")
		output.speak(_("Translated"))

	def spellcheck(self, text):
		checker = SpellChecker.spellchecker.spellChecker(text)
		if hasattr(checker, "fixed_text"):
			self.send_message("set", control="post_view", value=checker.fixed_text)
			self.send_message("focus_control", control="post_view")
		checker.clean()

	def open_attachment(self, index):
		attachment = self.attachments[index]
		if attachment["type"] == "audio":
			a = audio.displayAudioPresenter(session=self.session, postObject=[attachment["audio"]], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
		elif attachment["type"] == "link":
			output.speak(_("Opening URL..."), True)
			webbrowser.open_new_tab(attachment["link"]["url"])
		elif attachment["type"] == "doc":
			output.speak(_("Opening document in web browser..."))
			webbrowser.open(attachment["doc"]["url"])
		elif attachment["type"] == "video":
			# it seems VK doesn't like to attach video links as normal URLS, so we'll have to
			# get the full video object and use its "player" key  which will open a webbrowser in their site with a player for the video.
			# see https://vk.com/dev/attachments_w and and https://vk.com/dev/video.get
			# However, the flash player  isn't good  for visually impaired people (when you press play you won't be able to close the window with alt+f4), so it could be good to use the HTML5 player.
			# For firefox,  see https://addons.mozilla.org/ru/firefox/addon/force-html5-video-player-at-vk/
			# May be I could use a dialogue here for inviting people to use this addon in firefox. It seems it isn't possible to use this html5 player from the player URL.
			object_id = "{0}_{1}".format(attachment["video"]["owner_id"], attachment["video"]["id"])
			video_object = self.session.vk.client.video.get(owner_id=attachment["video"]["owner_id"], videos=object_id)
			video_object = video_object["items"][0]
			output.speak(_("Opening video in web browser..."), True)
			webbrowser.open_new_tab(video_object["player"])
		elif attachment["type"] == "photo":
			output.speak(_("Opening photo in web browser..."), True)
			# Possible photo sizes for looking in the attachment information. Try to use the biggest photo available.
			possible_sizes = [1280, 604, 130, 75]
			url = ""
			for i in possible_sizes:
				if "photo_{0}".format(i,) in attachment["photo"]:
					url = attachment["photo"]["photo_{0}".format(i,)]
					break
			if url != "":
				webbrowser.open_new_tab(url)
		elif attachment["type"] == "poll":
			a = poll.displayPollPresenter(session=self.session, poll=attachment, interactor=interactors.displayPollInteractor(), view=views.displayPoll())
		elif attachment["type"] == "article":
			a = article.displayArticlePresenter(session=self.session, postObject=[attachment["article"]], interactor=interactors.displayArticleInteractor(), view=views.displayArticle())
		else:
			log.error("Unhandled attachment: %r" % (attachment,))

	def __del__(self):
		if hasattr(self, "worker"):
			self.worker.finished.set()

	def clear_comments_list(self):
		self.send_message("clean_list", list="comments")
		self.get_comments()

	def show_likes(self):
		""" show likes for the specified post."""
		data = dict(type="post", owner_id=self.post[self.user_identifier], item_id=self.post["id"], extended=True, count=100, skip_own=True)
		result = self.session.vk.client.likes.getList(**data)
		if result["count"] > 0:
			post = {"source_id": self.post[self.user_identifier], "friends": {"items": result["items"]}}
			pub.sendMessage("open-post", post_object=post, controller_="displayFriendship", vars=dict(caption=_("people who liked this")))

	def show_shares(self):
		data = dict(type="post", owner_id=self.post[self.user_identifier], item_id=self.post["id"], extended=True, count=1000, skip_own=True, filter="copies")
		result = self.session.vk.client.likes.getList(**data)
		if result["count"] > 0:
			post = {"source_id": self.post[self.user_identifier], "friends": {"items": result["items"]}}
			pub.sendMessage("open-post", post_object=post, controller_="displayFriendship", vars=dict(caption=_("people who shared this")))