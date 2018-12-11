# -*- coding: utf-8 -*-
import re
import os
import cStringIO
import threading
import arrow
import messages
import requests
import languageHandler
import widgetUtils
import output
import wx
import webbrowser
import logging
from sessionmanager import session # We'll use some functions from there
from sessionmanager import utils
from pubsub import pub
from wxUI.dialogs import postDialogs, urlList, profiles
from extra import SpellChecker, translator
from mysc.thread_utils import call_threaded
from wxUI import menus

log = logging.getLogger("controller.post")

def get_user(id, profiles):
	""" Returns an user name and last name  based in the id receibed."""
	for i in profiles:
		if i["id"] == id:
			return u"{0} {1}".format(i["first_name"], i["last_name"])
	# Translators: This string is used when socializer can't find the right user information.
	return _(u"Unknown username")

def get_message(status):
	message = ""
	if status.has_key("text"):
		message = utils.clean_text(status["text"])
	return message

class postController(object):
	""" Base class for post representation."""

	def __init__(self, session, postObject):
		super(postController, self).__init__()
		self.session = session
		self.post = postObject
		# Posts from newsfeed contains this source_id instead from_id in walls. Also it uses post_id and walls use just id.
		if self.post.has_key("source_id"):
			self.user_identifier = "source_id"
			self.post_identifier = "post_id"
		else:
			# In wall's posts, if someone has posted in user's wall, owner_id should be used instead from_id
			# This will help for retrieving comments, do likes, etc.
			if not self.post.has_key("owner_id"):
				self.user_identifier = "from_id"
			else:
				self.user_identifier = "owner_id"
			self.post_identifier = "id"
		self.dialog = postDialogs.post()
#		self.dialog.comments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.show_comment)
		widgetUtils.connect_event(self.dialog.like, widgetUtils.BUTTON_PRESSED, self.post_like)
		widgetUtils.connect_event(self.dialog.comment, widgetUtils.BUTTON_PRESSED, self.add_comment)
		widgetUtils.connect_event(self.dialog.tools, widgetUtils.BUTTON_PRESSED, self.show_tools_menu)
		widgetUtils.connect_event(self.dialog.repost, widgetUtils.BUTTON_PRESSED, self.post_repost)
#		self.dialog.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu, self.dialog.comments.list)
#		self.dialog.Bind(wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key, self.dialog.comments.list)
		self.worker = threading.Thread(target=self.load_all_components)
		self.worker.finished = threading.Event()
		self.worker.start()
		self.attachments = []
		self.load_images = False
		# We'll put images here, so it will be easier to work with them.
		self.images = []
		self.imageIndex = 0

	def get_comments(self):
		""" Get comments and insert them in a list."""
		user = self.post[self.user_identifier]
		id = self.post[self.post_identifier]
		self.comments = self.session.vk.client.wall.getComments(owner_id=user, post_id=id, need_likes=1, count=100, extended=1, preview_length=0)
		comments_ = []
		for i in self.comments["items"]:
			# If comment has a "deleted" key it should not be displayed, obviously.
			if "deleted" in i:
				continue
			from_ = get_user(i["from_id"], self.comments["profiles"])
			if i.has_key("reply_to_user"):
				extra_info = get_user(i["reply_to_user"], self.comments["profiles"])
				from_ = _(u"{0} > {1}").format(from_, extra_info)
			# As we set the comment reply properly in the from_ field, let's remove the first username from here if it exists.
			fixed_text = re.sub("^\[id\d+\|\D+\], ", "", i["text"])
			if len(fixed_text) > 140:
				text = fixed_text[:141]
			else:
				text = fixed_text
			original_date = arrow.get(i["date"])
			created_at = original_date.humanize(locale=languageHandler.getLanguage())
			likes = str(i["likes"]["count"])
			comments_.append((from_, text, created_at, likes))
		try:
			self.dialog.insert_comments(comments_)
		except wx.PyDeadObjectError:
			pass

	def get_post_information(self):
		from_ = self.session.get_user_name(self.post[self.user_identifier])
		if self.post.has_key("copy_history"):
			# Translators: {0} will be replaced with an user.
			title = _(u"repost from {0}").format(from_,)
		else:
			if self.post.has_key("from_id") and self.post.has_key("owner_id"):
				# Translators: {0} will be replaced with the user who is posting, and {1} with the wall owner.
				title = _(u"Post from {0} in the {1}'s wall").format(self.session.get_user_name(self.post["from_id"]), self.session.get_user_name(self.post["owner_id"]))
			else:
				title = _(u"Post from {0}").format(from_,)
		self.dialog.set_title(title)
		message = u""
		message = get_message(self.post)
		if self.post.has_key("copy_history"):
			nm = u"\n"
			for i in self.post["copy_history"]:
				nm += u"{0}: {1}\n\n".format(self.session.get_user_name(i["from_id"]),  get_message(i))
				self.get_attachments(i)
			message += nm
		self.dialog.set_post(message)
		self.get_attachments(self.post)
		self.check_image_load()

	def get_attachments(self, post):
		attachments = []
		if post.has_key("attachments"):
			for i in post["attachments"]:
				# We don't need the photos_list attachment, so skip it.
				if i["type"] == "photos_list":
					continue
				if i["type"] == "photo":
					if self.load_images == False: self.load_images = True
					self.images.append(i)
				attachments.append(utils.add_attachment(i))
				self.attachments.append(i)
		# Links in text are not treated like normal attachments, so we'll have to catch and add those to the list without title
		# We can't get a title because title is provided by the VK API and it will not work for links as simple text.
		urls = utils.find_urls_in_text(self.dialog.get("post_view"))
		if len(urls) > 0:
			links = []
			for i in urls:
				links.append({"link": {"title": _(U"Untitled link"), "url": i}, "type": "link"})
			for i in links:
				attachments.append(utils.add_attachment(i))
				self.attachments.append(i)
		if len(self.attachments) > 0:
			self.dialog.attachments.list.Enable(True)
			self.dialog.attachments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_attachment)
			self.dialog.insert_attachments(attachments)

	def check_image_load(self):
		if self.load_images and len(self.images) > 0 and self.session.settings["general"]["load_images"]:
			self.dialog.image.Enable(True)
			nav = False # Disable navigation controls in photos
			if len(self.images) > 1:
				nav = True
				widgetUtils.connect_event(self.dialog.previous_photo, widgetUtils.BUTTON_PRESSED, self.set_previous_image)
				widgetUtils.connect_event(self.dialog.next_photo, widgetUtils.BUTTON_PRESSED, self.set_next_image)
			self.dialog.enable_photo_controls(navigation=nav)
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
			log.exception("Error in loading image {0} in a list with {1} images".format(index, len(self.images)))
			return
		# Get's photo URL.
		url = self.get_photo_url(self.images[index]["photo"], "x")
		if url != "":
			img = requests.get(url)
			image = wx.Image(stream=cStringIO.StringIO(requests.get(url).content))
			try:
				self.dialog.image.SetBitmap(wx.Bitmap(image))
			except NameError:
				return
			self.dialog.SetClientSize(self.dialog.sizer.CalcMin())
			# Translators: {0} is the number of the current photo and {1} is the total number of photos.
			output.speak(_(u"Loaded photo {0} of {1}").format(index+1, len(self.images)))
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
			self.dialog.disable("comment")
		if self.post["likes"]["can_like"] == 0 and self.post["likes"]["user_likes"] == 0:
			self.dialog.disable("like")
		elif self.post["likes"]["user_likes"] == 1:
			self.dialog.set("like", _(u"&Dislike"))
		if self.post["likes"]["can_publish"] == 0:
			self.dialog.disable("repost")

	def post_like(self, *args, **kwargs):
		if self.post.has_key("owner_id") == False:
			user = int(self.post[self.user_identifier])
		else:
			user = int(self.post["owner_id"])
		id = int(self.post[self.post_identifier])
		if self.post.has_key("type"):
			type_ = self.post["type"]
		else:
			type_ = "post"
		if self.dialog.get("like") == _(u"&Dislike"):
			l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
			output.speak(_(u"You don't like this"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 2
			self.get_likes()
			self.dialog.set("like", _(u"&Like"))
		else:
			l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
			output.speak(_(u"You liked this"))
			self.dialog.set("like", _(u"&Dislike"))
			self.post["likes"]["count"] = l["likes"]
			self.post["likes"]["user_likes"] = 1
			self.get_likes()

	def post_repost(self, *args, **kwargs):
		object_id = "wall{0}_{1}".format(self.post[self.user_identifier], self.post[self.post_identifier])
		p = messages.post(session=self.session, title=_(u"Repost"), caption=_(u"Add your comment here"), text="")
		if p.message.get_response() == widgetUtils.OK:
			msg = p.message.get_text().encode("utf-8")
			self.session.vk.client.wall.repost(object=object_id, message=msg)

	def get_likes(self):
		try:
			self.dialog.set_likes(self.post["likes"]["count"])
		except wx.PyDeadObjectError:
			pass

	def get_reposts(self):
		try:
			self.dialog.set_shares(self.post["reposts"]["count"])
		except wx.PyDeadObjectError:
			pass

	def add_comment(self, *args, **kwargs):
		comment = messages.comment(session=self.session, title=_(u"Add a comment"), caption="", text="")
		if comment.message.get_response() == widgetUtils.OK:
			msg = comment.message.get_text().encode("utf-8")
			try:
				user = self.post[self.user_identifier]
				id = self.post[self.post_identifier]
				self.session.vk.client.wall.addComment(owner_id=user, post_id=id, text=msg)
				output.speak(_(u"You've posted a comment"))
				if self.comments["count"] < 100:
					self.clear_comments_list()
					self.get_comments()
			except Exception as msg:
				log.error(msg)

	def clear_comments_list(self):
		self.dialog.comments.clear()

	def show_comment(self, *args, **kwargs):
		c = comment(self.session, self.comments["data"][self.dialog.comments.get_selected()])
		c.dialog.get_response()

	def show_menu(self, *args, **kwargs):
		if self.dialog.comments.get_count() == 0: return
		menu = menus.commentMenu()
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.show_comment, menuitem=menu.open)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.comment_like, menuitem=menu.like)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.comment_unlike, menuitem=menu.unlike)
		self.dialog.PopupMenu(menu, self.dialog.comments.list.GetPosition())

	def show_menu_by_key(self, ev):
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			self.show_menu()

	def show_tools_menu(self, *args, **kwargs):
		menu = menus.toolsMenu()
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.open_url, menuitem=menu.url)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.translate, menuitem=menu.translate)
		widgetUtils.connect_event(self.dialog, widgetUtils.MENU, self.spellcheck, menuitem=menu.CheckSpelling)
		self.dialog.PopupMenu(menu, self.dialog.tools.GetPosition())

	def comment_like(self, *args, **kwargs):
		comment_id = self.comments["data"][self.dialog.comments.get_selected()]["id"]
		self.session.like(comment_id)
		output.speak(_(u"You do like this comment"))

	def comment_unlike(self, *args, **kwargs):
		comment_id = self.comments["data"][self.dialog.comments.get_selected()]["id"]
		self.session.unlike(comment_id)
		output.speak(_(u"You don't like this comment"))

	def translate(self, *args, **kwargs):
		dlg = translator.gui.translateDialog()
		if dlg.get_response() == widgetUtils.OK:
			text_to_translate = self.dialog.post_view.GetValue().encode("utf-8")
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			msg = translator.translator.translate(text_to_translate, target=dest)
			self.dialog.post_view.ChangeValue(msg)
			output.speak(_(u"Translated"))
		else:
			return

	def spellcheck(self, *args, **kwargs):
		text = self.dialog.post_view.GetValue()
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.dialog.post_view.ChangeValue(checker.fixed_text)

	def open_attachment(self, *args, **kwargs):
		index = self.dialog.attachments.get_selected()
		attachment = self.attachments[index]
		if attachment["type"] == "audio":
			a = audio(session=self.session, postObject=[attachment["audio"]])
			a.dialog.get_response()
			a.dialog.Destroy()
		if attachment["type"] == "link":
			output.speak(_(u"Opening URL..."), True)
			webbrowser.open_new_tab(attachment["link"]["url"])
		elif attachment["type"] == "doc":
			output.speak(_(u"Opening document in web browser..."))
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
			output.speak(_(u"Opening video in web browser..."), True)
			webbrowser.open_new_tab(video_object["player"])
		elif attachment["type"] == "photo":
			output.speak(_(u"Opening photo in web browser..."), True)
			# Possible photo sizes for looking in the attachment information. Try to use the biggest photo available.
			possible_sizes = [1280, 604, 130, 75]
			url = ""
			for i in possible_sizes:
				if attachment["photo"].has_key("photo_{0}".format(i,)):
					url = attachment["photo"]["photo_{0}".format(i,)]
					break
			if url != "":
				webbrowser.open_new_tab(url)
		else:
			log.debug("Unhandled attachment: %r" % (attachment,))

	def __del__(self):
		if hasattr(self, "worker"):
			self.worker.finished.set()

class comment(object):
	def __init__(self, session, comment_object):
		super(comment, self).__init__()
		self.session = session
		self.comment = comment_object
		self.dialog = postDialogs.comment()
		from_ = self.comment["from"]["name"]
		message = self.comment["message"]
		original_date = arrow.get(self.comment["created_time"], "YYYY-MM-DTHH:m:sZ", locale="en")
		created_at = original_date.humanize(locale=languageHandler.getLanguage())
		self.dialog.set_post(message)
		self.dialog.set_title(_(u"Comment from {0}").format(from_,))
		widgetUtils.connect_event(self.dialog.like, widgetUtils.BUTTON_PRESSED, self.post_like)
		call_threaded(self.get_likes)

	def get_likes(self):
		self.likes = self.session.fb.client.get_connections(id=self.comment["id"], connection_name="likes", summary=True)
		self.dialog.set_likes(self.likes["summary"]["total_count"])

	def post_like(self, *args, **kwargs):
		lk = self.session.like(self.comment["id"])
		self.get_likes()

class audio(postController):
	def __init__(self, session, postObject):
		self.added_audios = {}
		self.session = session
		self.post = postObject
		self.dialog = postDialogs.audio()
		widgetUtils.connect_event(self.dialog.list, widgetUtils.LISTBOX_CHANGED, self.handle_changes)
		self.load_audios()
		self.fill_information(0)
		widgetUtils.connect_event(self.dialog.download, widgetUtils.BUTTON_PRESSED, self.download)
		widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.play)
		widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.add_to_library)
		widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_from_library)

	def add_to_library(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		args = {}
		args["audio_id"] = post["id"]
		if post.has_key("album_id"):
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			self.added_audios[post["id"]] = audio
			self.dialog.change_state("add", False)
			self.dialog.change_state("remove", True)

	def remove_from_library(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		args = {}
		if self.added_audios.has_key(post["id"]):
			args["audio_id"] = self.added_audios[post["id"]]
			args["owner_id"] = self.session.user_id
		else:
			args["audio_id"] = post["id"]
			args["owner_id"] = post["owner_id"]
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			self.dialog.change_state("add", True)
			self.dialog.change_state("remove", False)
			if self.added_audios.has_key(post["id"]):
				self.added_audios.pop(post["id"])

	def fill_information(self, index):
		post = self.post[index]
		if post.has_key("artist"):
			self.dialog.set("artist", post["artist"])
		if post.has_key("title"):
			self.dialog.set("title", post["title"])
		if post.has_key("duration"):
			self.dialog.set("duration", utils.seconds_to_string(post["duration"]))
		self.dialog.set_title(u"{0} - {1}".format(post["title"], post["artist"]))
		call_threaded(self.get_lyrics)
		if  post["owner_id"] == self.session.user_id or self.added_audios.has_key(post["id"]) == True:
			self.dialog.change_state("remove", True)
			self.dialog.change_state("add", False)
		else:
			self.dialog.change_state("add", True)
			self.dialog.change_state("remove", False)

	def get_lyrics(self):
		post = self.post[self.dialog.get_audio()]
		if post.has_key("lyrics_id"):
			l = self.session.vk.client.audio.getLyrics(lyrics_id=int(post["lyrics_id"]))
			self.dialog.set("lyric", l["text"])
		else:
			self.dialog.change_state("lyric", False)

	def download(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		f = u"{0} - {1}.mp3".format(post["title"], post["artist"])
		path = self.dialog.get_destination_path(f)
		if path != None:
			pub.sendMessage("download-file", url=post["url"], filename=path)

	def play(self, *args, **kwargs):
		post = self.post[self.dialog.get_audio()]
		pub.sendMessage("play-audio", audio_object=post)

	def load_audios(self):
		for i in self.post:
			s = u"{0} - {1}. {2}".format(i["title"], i["artist"], utils.seconds_to_string(i["duration"]))
			self.dialog.insert_audio(s)
		self.dialog.list.SetSelection(0)
		if len(self.post) == 1:
			self.dialog.list.Enable(False)
			self.dialog.title.SetFocus()

	def handle_changes(self, *args, **kwargs):
		p = self.dialog.get_audio()
		self.fill_information(p)

class friendship(object):

	def __init__(self, session, post):
		self.session = session
		self.post = post
		self.dialog = postDialogs.friendship()
		list_of_friends = self.get_friend_names()
		from_ = self.session.get_user_name(self.post["source_id"])
		title = _(u"{0} added the following friends").format(from_,)
		self.dialog.set_title(title)
		self.set_friends_list(list_of_friends)

	def get_friend_names(self):
		self.friends = self.post["friends"]["items"]
		return [self.session.get_user_name(i["user_id"]) for i in self.friends]

	def set_friends_list(self, friendslist):
		for i in friendslist:
			self.dialog.friends.insert_item(False, *[i])

class userProfile(object):

	def __init__(self, session, user_id):
		self.person = None
		self.session = session
		self.user_id = user_id
		self.dialog = profiles.userProfile(title=_(u"Profile"))
		self.dialog.create_controls("main_info")
		self.dialog.realice()
		self.get_basic_information()
		if self.person != None:
			self.dialog.get_response()

	def get_basic_information(self):
		""" Gets and inserts basic user information.
		See https://vk.com/dev/users.get"""
		fields = "first_name, last_name, bdate, city, country, home_town, photo_200_orig, online,  site,  status, last_seen, occupation, relation, relatives, personal, connections, activities, interests, music, movies, tv, books, games, about, quotes, can_write_private_message"
		person = self.session.vk.client.users.get(user_ids=self.user_id, fields=fields)
		if len(person) == 0:
			return output.speak(_(u"Information for groups is not supported, yet."))
		person = person[0]
		print person
		# Gets full name.
		n = u"{0} {1}".format(person["first_name"], person["last_name"])
		# Gets birthdate.
		if person.has_key("bdate") and person["bdate"] != "":
			self.dialog.main_info.enable("bdate")
			if len(person["bdate"]) <= 5:
				d = arrow.get(person["bdate"], "D.m")
				self.dialog.main_info.set("bdate", d.format(_(u"MMMM D"), locale=languageHandler.getLanguage()))
			else:
				d = arrow.get(person["bdate"], "D.M.YYYY")
				self.dialog.main_info.set("bdate", d.format(_(u"MMMM D, YYYY"), locale=languageHandler.getLanguage()))
		# Gets current city and home town
		city = ""
		if person.has_key("home_town") and person["home_town"] != "":
			home_town = person["home_town"]
			self.dialog.main_info.enable("home_town")
			self.dialog.main_info.set("home_town", home_town)
		if person.has_key("city") and len(person["city"]) > 0:
			city = person["city"]["title"]
		if person.has_key("country") and person["country"] != "":
			if city != "":
				city = city+u", {0}".format(person["country"]["title"])
			else:
				city = person["country"]["title"]
			self.dialog.main_info.enable("city")
			self.dialog.main_info.set("city", city)
		self.dialog.main_info.set("name", n)
		self.dialog.SetTitle(_(u"{name}'s profile").format(name=n,))
		# Gets website
		if person.has_key("site") and person["site"] != "":
			self.dialog.main_info.enable("website")
			self.dialog.main_info.set("website", person["site"])
			self.dialog.main_info.enable("go_site")
			widgetUtils.connect_event(self.dialog.main_info.go_site, widgetUtils.BUTTON_PRESSED, self.visit_website)
		if person.has_key("status") and person["status"] != "":
			self.dialog.main_info.enable("status")
			self.dialog.main_info.set("status", person["status"])
		if person.has_key("occupation") and person["occupation"] != None:
			if person["occupation"]["type"] == "work": c1 = _(u"Work ")
			elif person["occupation"]["type"] == "school": c1 = _(u"Student ")
			elif person["occupation"]["type"] == "university": c1 = _(u"Student ")
			if person["occupation"].has_key("name") and person["occupation"]["name"] != "":
				c2 = _(u"In {0}").format(person["occupation"]["name"],)
			else:
				c2 = ""
			self.dialog.main_info.enable("occupation")
			self.dialog.main_info.set("occupation", c1+c2)
		if person.has_key("relation") and person["relation"] != 0:
			print person["relation"]
			if person["relation"] == 1:
				r =  _(u"Single")
			elif person["relation"] == 2:
				if person.has_key("relation_partner"):
					r = _(u"Dating with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
				else:
					r = _(u"Dating")
			elif person["relation"] == 3:
				r = _(u"Engaged with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
			elif person["relation"] == 4:
				r = _(u"Married with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
			elif person["relation"] == 5:
				r = _(u"It's complicated")
			elif person["relation"] == 6:
				r = _(u"Actively searching")
			elif person["relation"] == 7:
				r = _(u"In love")
			self.dialog.main_info.enable("relation")
			self.dialog.main_info.relation.SetLabel(_(u"Relationship: ")+r)
		if person.has_key("last_seen") and person["last_seen"] != False:
			original_date = arrow.get(person["last_seen"]["time"])
			# Translators: This is the date of last seen
			last_seen = _(u"{0}").format(original_date.humanize(locale=languageHandler.getLanguage()),)
			self.dialog.main_info.enable("last_seen")
			self.dialog.main_info.set("last_seen", last_seen)
		log.info("getting info...")
		self.person = person
		self.dialog.SetClientSize(self.dialog.sizer.CalcMin())

	def visit_website(self, *args, **kwargs):
		output.speak(_(u"Opening website..."))
		webbrowser.open_new_tab(self.person["site"])