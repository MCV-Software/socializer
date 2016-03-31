# -*- coding: utf-8 -*-
import wx
import widgetUtils
import messages
import utils
import posts
import player
import output
from wxUI.tabs import home
from pubsub import pub
from sessionmanager import session
from mysc.thread_utils import call_threaded
from wxUI import commonMessages

class baseBuffer(object):
	""" a basic representation of a buffer. Other buffers should be derived from this class"""
	def __init__(self, parent=None, name="", session=None, composefunc=None, *args, **kwargs):
		""" parent wx.Treebook: parent for the buffer panel,
		name str: Name for saving this buffer's data in the local storage variable,
		session sessionmanager.session.vkSession: Session for performing operations in the Vk API. This session should be logged in when this class is instanciated.
		composefunc str: This function will be called for composing the result which will be put in the listCtrl. Composefunc should existss in the sessionmanager.session module.
		args and kwargs will be passed to get_items()"""
		super(baseBuffer, self).__init__()
		self.args = args
		self.kwargs = kwargs
		self.create_tab(parent)
		# Add the name to the new control so we could look for it when needed.
		self.tab.name = name
		self.session = session
		self.compose_function = composefunc
		self.update_function = "get_page"
		self.name = name
		self.connect_events()

	def create_tab(self, parent):
		""" Creates the Wx panel."""
		self.tab = home.homeTab(parent)

	def insert(self, item, reversed=False):
		""" Add a new item to the list. Uses session.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
		item_ = getattr(session, self.compose_function)(item, self.session)
		self.tab.list.insert_item(reversed, *item_)

	def get_items(self, show_nextpage=False):
		""" Retrieves items from the VK API. This function is called repeatedly by the main controller and users could call it implicitly as well with the update buffer option.
		show_nextpage boolean: If it's true, it will try to load previous results."""
		num = getattr(self.session, "get_newsfeed")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		else:
			if num > 0:
				[self.insert(i, False) for i in self.session.db[self.name]["items"][:num]]

	def get_more_items(self):
		self.get_items(show_nextpage=True)

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
		p.message.Destroy()

	def connect_events(self):
		widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
		widgetUtils.connect_event(self.tab.list.list, widgetUtils.KEYPRESS, self.get_event)

	def get_event(self, ev):
		if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown() and ev.ShiftDown(): event = "pause_audio"
		elif ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "play_audio"
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
			pub.sendMessage("play-audio", audio_object=post["audio"]["items"][0])

	def open_post(self):
		post = self.session.db[self.name]["items"][self.tab.list.get_selected()]
		if post.has_key("type") and post["type"] == "audio":
			a = posts.audio(self.session, post["audio"]["items"])
			a.dialog.get_response()
			a.dialog.Destroy()
		elif post.has_key("type") and post["type"] == "friend":
			pub.sendMessage("open-post", post_object=post, controller_="friendship")
		else:
			pub.sendMessage("open-post", post_object=post, controller_="postController")

	def pause_audio(self, *args, **kwargs):
		player.player.pause()

	def remove_buffer(self): return False

class feedBuffer(baseBuffer):

	def get_items(self, show_nextpage=False):
		num = getattr(self.session, "get_page")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		print num
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]

class audioBuffer(feedBuffer):
	def create_tab(self, parent):
		self.tab = home.audioTab(parent)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		widgetUtils.connect_event(self.tab.play_all, widgetUtils.BUTTON_PRESSED, self.play_all)
		super(audioBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		pub.sendMessage("play-audio", audio_object=self.session.db[self.name]["items"][selected])

	def open_post(self):
		selected = self.tab.list.get_selected()
		audios = [self.session.db[self.name]["items"][selected]]
		a = posts.audio(self.session, audios)
		a.dialog.get_response()
		a.dialog.Destroy()

	def play_all(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		audios = [i for i in self.session.db[self.name]["items"][selected:]]
		pub.sendMessage("play-audios", audios=audios)

	def remove_buffer(self):
		if "me_audio" == self.name or "popular_audio" == self.name or "recommended_audio" == self.name:
			output.speak(_(u"This buffer can't be deleted"))
			return False
		else:
			dlg = commonMessages.remove_buffer()
			if dlg == widgetUtils.YES:
				self.session.db.pop(self.name)
				return True
			else:
				return False


	def get_more_items(self, *args, **kwargs):
		output.speak(_(u"This buffer doesn't support getting more items."))

class empty(object):

	def __init__(self, name=None, parent=None, *args, **kwargs):
		self.tab = home.empty(parent=parent, name=name)
		self.name = name

	def get_items(self, *args, **kwargs):
		pass

	def get_more_items(self, *args, **kwargs):
		output.speak(_(u"This buffer doesn't support getting more items."))

	def remove_buffer(self): return False
