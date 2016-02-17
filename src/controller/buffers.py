# -*- coding: utf-8 -*-
import wx
import widgetUtils
import messages
import utils
import posts
import player
from wxUI.tabs import home
from pubsub import pub
from sessionmanager import session
from mysc.thread_utils import call_threaded

class baseBuffer(object):
	def __init__(self, parent=None, name="", session=None, composefunc=None, *args, **kwargs):
		super(baseBuffer, self).__init__()
		self.args = args
		self.kwargs = kwargs
		self.create_tab(parent)
		self.tab.name = name
		self.session = session
		self.compose_function = composefunc
		self.update_function = "get_page"
		self.name = name
		self.connect_events()

	def create_tab(self, parent):
		self.tab = home.homeTab(parent)

	def insert(self, item, reversed=False):
		item_ = getattr(session, self.compose_function)(item, self.session)
		self.tab.list.insert_item(reversed, *item_)

	def get_items(self, no_next=True):
		num = getattr(self.session, "get_newsfeed")(no_next=no_next, name=self.name, *self.args, **self.kwargs)
		print num
		if no_next == True:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				[self.insert(i, True) for i in self.session.db[self.name]["items"][num:]]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]

	def post(self, *args, **kwargs):
		p = messages.post(title=_(u"Write your post"), caption="", text="")
		if p.message.get_response() == widgetUtils.OK:
			msg = p.message.get_text().encode("utf-8")
			privacy_opts = p.get_privacy_options()
			attachments = ""
			urls = utils.find_urls_in_text(msg)
			if len(urls) != 0:
				if len(attachments) == 0: attachments = urls[0]
				else: attachments += urls[0]
				msg = msg.replace(urls[0], "")
			self.session.post_wall_status(message=msg, friends_only=privacy_opts, attachments=attachments)
			pub.sendMessage("posted", buffer=self.name)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
		widgetUtils.connect_event(self.tab.list.list, widgetUtils.KEYPRESS, self.get_event)

	def get_event(self, ev):
		if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "play_audio"
		elif ev.GetKeyCode() == wx.WXK_RETURN: event = "open_post"
		elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
		elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
		else:
			event = None
			ev.Skip()
		if event != None:
			try:
				getattr(self, event)()
			except AttributeError:
				pass

	def volume_down(self):
		player.player.volume = player.player.volume-5

	def volume_up(self):
		player.player.volume = player.player.volume+5

	def play_audio(self, *args, **kwargs):
		post = self.session.db[self.name]["items"][self.tab.list.get_selected()]
		if post.has_key("type") and post["type"] == "audio":
			pub.sendMessage("play-audio", audio_object=post["audio"][1]["url"])

class feedBuffer(baseBuffer):

	def get_items(self, no_next=True):
		num = getattr(self.session, "get_page")(no_next=no_next, name=self.name, *self.args, **self.kwargs)
		print num
		if no_next == True:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				[self.insert(i, True) for i in self.session.db[self.name]["items"][-num:]]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]


class audioBuffer(feedBuffer):
	def create_tab(self, parent):
		self.tab = home.audioTab(parent)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		super(audioBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		pub.sendMessage("play-audio", audio_object=self.session.db[self.name]["items"][selected]["url"])

	def open_post(self):
		selected = self.tab.list.get_selected()
		a = posts.audio(self.session, self.session.db[self.name]["items"][selected])
		a.dialog.get_response()

