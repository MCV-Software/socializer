# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import os
import six
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
from .import base
from .postCreation import createPostPresenter

log = logging.getLogger(__file__)

def get_user(id, profiles):
	""" Returns an user name and last name  based in the id receibed."""
	for i in profiles:
		if i["id"] == id:
			return "{0} {1}".format(i["first_name"], i["last_name"])
	# Translators: This string is used when socializer can't find the right user information.
	return _("Unknown username")

def get_message(status):
	message = ""
	if "text" in status:
		message = renderers.clean_text(status["text"])
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
		self.worker = threading.Thread(target=self.load_all_components)
		self.worker.finished = threading.Event()
		self.worker.start()
		self.attachments = []
		self.load_images = False
		# We'll put images here, so it will be easier to work with them.
		self.images = []
		self.imageIndex = 0
		self.run()

	def get_comments(self):
		""" Get comments and insert them in a list."""
		user = self.post[self.user_identifier]
		id = self.post[self.post_identifier]
		self.comments = self.session.vk.client.wall.getComments(owner_id=user, post_id=id, need_likes=1, count=100, extended=1, preview_length=0, thread_items_count=10)
		comments_ = []
		for i in self.comments["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = get_user(i["from_id"], self.comments["profiles"])
			if "reply_to_user" in i:
				extra_info = get_user(i["reply_to_user"], self.comments["profiles"])
				from_ = _("{0} > {1}").format(from_, extra_info)
			# As we set the comment reply properly in the from_ field, let's remove the first username from here if it exists.
			fixed_text = re.sub("^\[id\d+\|\D+\], ", "", i["text"])
			if len(fixed_text) > 140:
				text = fixed_text[:141]
			else:
				text = fixed_text
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(i["likes"]["count"])
			replies = str(i["thread"]["count"])
			comments_.append((from_, text, created_at, likes, replies))
		self.send_message("add_items", control="comments", items=comments_)

	def get_post_information(self):
		from_ = self.session.get_user_name(self.post[self.user_identifier])
		if "copy_history" in self.post:
			# Translators: {0} will be replaced with an user.
			title = _("repost from {0}").format(from_,)
		else:
			if ("from_id" in self.post and "owner_id" in self.post) and (self.post["from_id"] != self.post["owner_id"]):
				# Translators: {0} will be replaced with the user who is posting, and {1} with the wall owner.
				title = _("Post from {0} in the {1}'s wall").format(self.session.get_user_name(self.post["from_id"]), self.session.get_user_name(self.post["owner_id"]))
			else:
				title = _("Post from {0}").format(from_,)
		self.send_message("set_title", value=title)
		message = ""
		# Retrieve again the post, so we'll make sure to get the most up to date information.
		# And we add a counter for views.
		post = self.session.vk.client.wall.getById(posts="{owner_id}_{post_id}".format(owner_id=self.post[self.user_identifier], post_id=self.post[self.post_identifier]))
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
				nm += "{0}: {1}\n\n".format(self.session.get_user_name(i["from_id"]),  get_message(i))
				self.get_attachments(i, get_message(i))
			message += nm
		self.send_message("set", control="post_view", value=message)
		self.get_attachments(self.post, message)
		self.check_image_load()

	def get_attachments(self, post, text):
		attachments = []
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
		self.get_post_information()
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
			msg = p.text
			self.session.vk.client.wall.repost(object=object_id, message=msg)

	def get_likes(self):
		self.send_message("set_label", control="likes", label=_("{0} people like this").format(self.post["likes"]["count"],))

	def get_reposts(self):
		self.send_message("set_label", control="shares", label=_("Shared {0} times").format(self.post["reposts"]["count"],))

	def add_comment(self):
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Add a comment"), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			owner_id = self.post[self.user_identifier]
			post_id = self.post[self.post_identifier]
			call_threaded(self.do_last, comment, owner_id=owner_id, post_id=post_id)

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
		try:
			result = self.session.vk.client.wall.createComment(**kwargs)
			comment_object = self.session.vk.client.wall.getComment(comment_id=result["comment_id"], owner_id=kwargs["owner_id"])["items"][0]
			from_ = self.session.get_user_name(comment_object["from_id"])
			if "reply_to_user" in comment_object:
				extra_info = self.session.get_user_name(comment_object["reply_to_user"])
				from_ = _("{0} > {1}").format(from_, extra_info)
			# As we set the comment reply properly in the from_ field, let's remove the first username from here if it exists.
			fixed_text = re.sub("^\[id\d+\|\D+\], ", "", comment_object["text"])
			if len(fixed_text) > 140:
				text = fixed_text[:141]
			else:
				text = fixed_text
			original_date = arrow.get(comment_object["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(comment_object["likes"]["count"])
			replies = ""
			item = (from_, text, created_at, likes, replies)
			if hasattr(self, "comments"):
				self.comments["items"].append(comment_object)
			else:
				if "items" not in self.post["thread"]:
					self.post["thread"]["items"] = []
				self.post["thread"]["items"].append(comment_object)
			self.send_message("add_items", control="comments", items=[item])
			output.speak(_("You've posted a comment"))
		except IndexError as msg:
			log.error(msg)

	def upload_attachments(self, attachments):
		""" Upload attachments to VK before posting them.
		Returns attachments formatted as string, as required by VK API.
		Currently this function only supports photos and audios."""
		# To do: Check the caption and description fields for this kind of attachments.
		local_attachments = ""
		uploader = upload.VkUpload(self.session.vk.session_object)
		for i in attachments:
			if i["from"] == "online":
				local_attachments += "{0}{1}_{2},".format(i["type"], i["owner_id"], i["id"])
			elif i["from"] == "local" and i["type"] == "photo":
				photos = i["file"]
				description = i["description"]
				r = uploader.photo_wall(photos, caption=description)
				id = r[0]["id"]
				owner_id = r[0]["owner_id"]
				local_attachments += "photo{0}_{1},".format(owner_id, id)
			elif i["from"] == "local" and i["type"] == "audio":
				audio = i["file"]
				title = "untitled"
				artist = "unnamed"
				if "artist" in i:
					artist = i["artist"]
				if "title" in i:
					title = i["title"]
				r = uploader.audio(audio, title=title, artist=artist)
				id = r["id"]
				owner_id = r["owner_id"]
				local_attachments += "audio{0}_{1},".format(owner_id, id)
		return local_attachments

	def reply(self, comment):
		c = self.comments["items"][comment]
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {username}").format(username=self.session.get_user_name(c["from_id"]),), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			call_threaded(self.do_last, comment, owner_id=c["owner_id"], reply_to_comment=c["id"], post_id=c["post_id"], reply_to_user=c["owner_id"])

	def show_comment(self, comment_index):
		c = self.comments["items"][comment_index]
		c["post_id"] = self.post[self.post_identifier]
		a = displayCommentPresenter(session=self.session, postObject=c, interactor=interactors.displayPostInteractor(), view=views.displayComment())

	def translate(self, text, language):
		msg = translator.translator.translate(text, language)
		self.send_message("set", control="post_view", value=msg)
		self.send_message("focus_control", control="post_view")
		output.speak(_("Translated"))

	def spellcheck(self, text):
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.send_message("set", control="post_view", value=checker.fixed_text)
			self.send_message("focus_control", control="post_view")
		checker.clean()

	def open_attachment(self, index):
		attachment = self.attachments[index]
		if attachment["type"] == "audio":
			a = displayAudioPresenter(session=self.session, postObject=[attachment["audio"]], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
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
		else:
			log.debug("Unhandled attachment: %r" % (attachment,))

	def __del__(self):
		if hasattr(self, "worker"):
			self.worker.finished.set()

	def clear_comments_list(self):
		self.send_message("clean_list", list="comments")
		self.get_comments()

class displayCommentPresenter(displayPostPresenter):

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
		self.run()

	def load_all_components(self):
		self.get_post_information()
		self.get_likes()
		self.send_message("disable_control", control="comment")
		self.get_comments()
		if self.post["likes"]["can_like"] == 0 and self.post["likes"]["user_likes"] == 0:
			self.send_message("disable_control", "like")
		elif self.post["likes"]["user_likes"] == 1:
			self.send_message("set_label", control="like", label=_("&Dislike"))

	def get_post_information(self):
		from_ = self.session.get_user_name(self.post[self.user_identifier])
		if ("from_id" in self.post and "owner_id" in self.post):
			# Translators: {0} will be replaced with the user who is posting, and {1} with the wall owner.
			title = _("Comment from {0} in the {1}'s post").format(self.session.get_user_name(self.post["from_id"]), self.session.get_user_name(self.post["owner_id"]))
		self.send_message("set_title", value=title)
		message = ""
		message = get_message(self.post)
		self.send_message("set", control="post_view", value=message)
		self.get_attachments(self.post, message)
		self.check_image_load()

	def reply(self):
		comment = createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Reply to {username}").format(username=self.session.get_user_name(self.post["from_id"]),), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			call_threaded(self.do_last, comment, owner_id=self.post["owner_id"], reply_to_comment=self.post["id"], post_id=self.post["post_id"], reply_to_user=self.post["owner_id"])

	def get_comments(self):
		""" Get comments and insert them in a list."""
		comments_ = []
		if "thread" not in self.post:
			return
		for i in self.post["thread"]["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = self.session.get_user_name(i["from_id"])
			if "reply_to_user" in i:
				extra_info = self.session.get_user_name(i["reply_to_user"])
				from_ = _("{0} > {1}").format(from_, extra_info)
			# As we set the comment reply properly in the from_ field, let's remove the first username from here if it exists.
			fixed_text = re.sub("^\[id\d+\|\D+\], ", "", i["text"])
			if len(fixed_text) > 140:
				text = fixed_text[:141]
			else:
				text = fixed_text
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.curLang[:2])
			likes = str(i["likes"]["count"])
			replies = ""
			comments_.append((from_, text, created_at, likes, replies))
		self.send_message("add_items", control="comments", items=comments_)

	def show_comment(self, comment_index):
		c = self.post["thread"]["items"][comment_index]
		c["post_id"] = self.post["post_id"]
		a = displayCommentPresenter(session=self.session, postObject=c, interactor=interactors.displayPostInteractor(), view=views.displayComment())
		self.clear_comments_list()

class displayAudioPresenter(base.basePresenter):
	def __init__(self, session, postObject, view, interactor):
		super(displayAudioPresenter, self).__init__(view=view, interactor=interactor, modulename="display_audio")
		self.added_audios = {}
		self.session = session
		self.post = postObject
		self.load_audios()
		self.fill_information(0)
		self.run()

	def add_to_library(self, audio_index):
		post = self.post[audio_index]
		args = {}
		args["audio_id"] = post["id"]
		if "album_id" in post:
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			self.added_audios[post["id"]] = audio
			self.send_message("disable_control", control="add")
			self.send_message("enable_control", control="remove")

	def remove_from_library(self, audio_index):
		post = self.post[audio_index]
		args = {}
		if post["id"] in self.added_audios:
			args["audio_id"] = self.added_audios[post["id"]]
			args["owner_id"] = self.session.user_id
		else:
			args["audio_id"] = post["id"]
			args["owner_id"] = post["owner_id"]
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			self.send_message("enable_control", control="add")
			self.send_message("disable_control", control="remove")
			if post["id"] in self.added_audios:
				self.added_audios.pop(post["id"])

	def fill_information(self, index):
		post = self.post[index]
		if "artist" in post:
			self.send_message("set", control="artist", value=post["artist"])
		if "title" in post:
			self.send_message("set", control="title", value=post["title"])
		if "duration" in post:
			self.send_message("set", control="duration", value=utils.seconds_to_string(post["duration"]))
		self.send_message("set_title", value="{0} - {1}".format(post["title"], post["artist"]))
		call_threaded(self.get_lyrics, index)
		if  post["owner_id"] == self.session.user_id or (post["id"] in self.added_audios) == True:
			self.send_message("enable_control", control="remove")
			self.send_message("disable_control", control="add")
		else:
			self.send_message("enable_control", control="add")
			self.send_message("disable_control", control="remove")

	def get_lyrics(self, audio_index):
		post = self.post[audio_index]
		if "lyrics_id" in post:
			l = self.session.vk.client.audio.getLyrics(lyrics_id=int(post["lyrics_id"]))
			self.send_message("set", control="lyric", value=l["text"])
		else:
			self.send_message("disable_control", control="lyric")

	def get_suggested_filename(self, audio_index):
		post = self.post[audio_index]
		return "{0} - {1}.mp3".format(post["title"], post["artist"])

	def download(self, audio_index, path):
		post = self.post[audio_index]
		if path != None:
			pub.sendMessage("download-file", url=post["url"], filename=path)

	def play(self, audio_index):
		post = self.post[audio_index]
		pub.sendMessage("play-audio", audio_object=post)

	def load_audios(self):
		audios = []
		for i in self.post:
			s = "{0} - {1}. {2}".format(i["title"], i["artist"], utils.seconds_to_string(i["duration"]))
			audios.append(s)
		self.send_message("add_items", control="list", items=audios)
		if len(self.post) == 1:
			self.send_message("disable_control", control="list")
			self.send_message("focus_control", control="title")

	def handle_changes(self, audio_index):
		self.fill_information(audio_index)

class displayFriendshipPresenter(base.basePresenter):

	def __init__(self, session, postObject, view, interactor):
		self.session = session
		self.post = postObject
		super(displayFriendshipPresenter, self).__init__(view=view, interactor=interactor, modulename="display_friendship")
		list_of_friends = self.get_friend_names()
		from_ = self.session.get_user_name(self.post["source_id"])
		title = _("{0} added the following friends").format(from_,)
		self.send_message("set_title", value=title)
		self.set_friends_list(list_of_friends)
		self.run()

	def get_friend_names(self):
		self.friends = self.post["friends"]["items"]
		return [self.session.get_user_name(i["user_id"]) for i in self.friends]

	def set_friends_list(self, friendslist):
		self.send_message("add_items", control="friends", items=friendslist)