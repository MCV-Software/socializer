# -*- coding: utf-8 -*-
import os
import arrow
import messages
import languageHandler
import widgetUtils
import output
import wx
import webbrowser
import utils
from sessionmanager import session # We'll use some functions from there
from pubsub import pub
from wxUI.dialogs import postDialogs, urlList
from extra import SpellChecker, translator
from mysc.thread_utils import call_threaded
from wxUI import menus

class postController(object):
	def __init__(self, session, postObject):
		super(postController, self).__init__()
		self.session = session
		self.post = postObject
		self.dialog = postDialogs.post()
		self.dialog.comments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.show_comment)
#  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
#  widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
		widgetUtils.connect_event(self.dialog.like, widgetUtils.BUTTON_PRESSED, self.post_like)
		widgetUtils.connect_event(self.dialog.comment, widgetUtils.BUTTON_PRESSED, self.add_comment)
		widgetUtils.connect_event(self.dialog.tools, widgetUtils.BUTTON_PRESSED, self.show_tools_menu)
		self.dialog.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu, self.dialog.comments.list)
		self.dialog.Bind(wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key, self.dialog.comments.list)
#		call_threaded(self.load_all_components)
		self.get_post_information()

	def get_post_information(self):
		if self.post.has_key("type"):
			if self.post["type"] == "post":
				from_ = self.session.get_user_name(self.post["source_id"])
				title = _(u"Post from {0}").format(from_,)
				self.dialog.set_title(title)
				message = u""
				if self.post.has_key("text"):
					message = self.post["text"]
				if self.post.has_key("attachment"):
					print self.post["attachment"].keys()
				message = message+session.add_attachment(self.post["attachment"])
				self.dialog.set_post(message)

	def load_all_components(self):
		self.get_likes()
		self.get_shares()
		self.get_comments()

	def post_like(self, *args, **kwargs):
		lk = self.session.like(self.post["id"])
		self.get_likes()

	def get_likes(self):
		self.likes = self.session.fb.client.get_connections(id=self.post["id"], connection_name="likes", summary=True)
		self.dialog.set_likes(self.likes["summary"]["total_count"])

	def get_shares(self):
		self.shares = self.session.fb.client.get_connections(id=self.post["id"], connection_name="sharedposts")
		self.dialog.set_shares(str(len(self.shares["data"])))

	def get_comments(self):
		self.comments = self.session.fb.client.get_connections(id=self.post["id"], connection_name="comments", filter="stream")
		comments = []
		for i in self.comments["data"]:
			from_ = i["from"]["name"]
			if len(i["message"]) > 100:
				comment = i["message"][:100]
			else:
				comment = i["message"]
			original_date = arrow.get(i["created_time"], "YYYY-MM-DTHH:m:sZ", locale="en")
			created_at = original_date.humanize(locale=languageHandler.getLanguage())
			likes = str(i["like_count"])
			comments.append([from_, comment, created_at, likes,])
		self.dialog.insert_comments(comments)

	def add_comment(self, *args, **kwargs):
		comment = messages.comment(title=_(u"Add a comment"), caption="", text="")
		if comment.message.get_response() == widgetUtils.OK:
			msg = comment.message.get_text().encode("utf-8")
			try:
				self.session.fb.client.put_comment(self.post["id"], msg)
				output.speak(_(u"You've posted a comment"))
				if len(self.comments["data"]) < 25:
					self.clear_comments_list()
					self.get_comments()
			except Exception as msg:
				print msg

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
			source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
			dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
			msg = translator.translator.translate(text_to_translate, source, dest)
			self.dialog.post_view.ChangeValue(msg)
			output.speak(_(u"Translated"))
		else:
			return

	def spellcheck(self, *args, **kwargs):
		text = self.dialog.post_view.GetValue()
		checker = SpellChecker.spellchecker.spellChecker(text, "")
		if hasattr(checker, "fixed_text"):
			self.dialog.post_view.ChangeValue(checker.fixed_text)

	def open_url(self, *args, **kwargs):
		text = self.dialog.post_view.GetValue()
		urls = find_urls(text)
		url = None
		if len(urls) == 0: return
		if len(urls) == 1:
			url = urls[0]
		elif len(urls) > 1:
			url_list = urlList.urlList()
			url_list.populate_list(urls)
			if url_list.get_response() == widgetUtils.OK:
				url = urls[url_list.get_item()]
		if url != None:
			output.speak(_(u"Opening URL..."), True)
			webbrowser.open_new_tab(url)

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
		self.session = session
		self.post = postObject
		self.dialog = postDialogs.audio()
		self.fill_information()
		widgetUtils.connect_event(self.dialog.download, widgetUtils.BUTTON_PRESSED, self.download)
		widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.play)

	def fill_information(self):
		if self.post.has_key("artist"):
			self.dialog.set("artist", self.post["artist"])
		if self.post.has_key("title"):
			self.dialog.set("title", self.post["title"])
		if self.post.has_key("duration"):
			self.dialog.set("duration", utils.seconds_to_string(self.post["duration"]))
		self.dialog.set_title(u"{0} - {1}".format(self.post["title"], self.post["artist"]))
		call_threaded(self.get_lyrics)

	def get_lyrics(self):
		if self.post.has_key("lyrics_id"):
			l = self.session.vk.client.audio.getLyrics(lyrics_id=int(self.post["lyrics_id"]))
			self.dialog.set("lyric", l["text"])

	def download(self, *args, **kwargs):
		f = u"{0} - {1}.mp3".format(self.post["title"], self.post["artist"])
		path = self.dialog.get_destination_path(f)
		if path != None:
			pub.sendMessage("download-file", url=self.post["url"], filename=path)

	def play(self, *args, **kwargs):
		pub.sendMessage("play-audio", audio_object=self.post["url"])

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
		self.friends = self.post["friends"][1:]
		return [self.session.get_user_name(i["uid"]) for i in self.friends]

	def set_friends_list(self, friendslist):
		for i in friendslist:
			self.dialog.friends.insert_item(False, *[i])
