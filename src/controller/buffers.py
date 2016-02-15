# -*- coding: utf-8 -*-
import widgetUtils
import messages
import player
import utils
from wxUI.tabs import home
from pubsub import pub
from sessionmanager import session

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
				[self.insert(i, True) for i in self.session.db[self.name]["items"][-num:]]
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
		widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)

	def play_audio(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		player.player.play(self.session.db[self.name]["items"][selected]["url"])

player.setup()