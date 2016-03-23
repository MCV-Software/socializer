# -*- coding: utf-8 -*-
import utils
import widgetUtils
import messages
import buffers
import player
import posts
from pubsub import pub
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded
from sessionmanager import session
from wxUI import (mainWindow, commonMessages)
from update import updater

class Controller(object):

	def search(self, tab_name):
		for i in xrange(0, len(self.buffers)):
			if self.buffers[i].name == tab_name:
				return self.buffers[i]
		return False

	def get_current_buffer(self):
		""" Get the current bufferObject"""
		buffer = self.window.get_current_buffer()
		if hasattr(buffer, "name"):
			buffer = self.search(buffer.name)
			return buffer

	def __init__(self):
		super(Controller, self).__init__()
		self.buffers = []
		player.setup()
		self.window = mainWindow.mainWindow()
		self.window.change_status(_(u"Ready"))
		self.session = session.sessions[session.sessions.keys()[0]]
		self.create_controls()
		self.window.Show()
		self.connect_events()
		call_threaded(updater.do_update)

	def create_controls(self):
		home = buffers.baseBuffer(parent=self.window.tb, name="home_timeline", session=self.session, composefunc="compose_new", endpoint="newsfeed")
		self.buffers.append(home)
		self.window.add_buffer(home.tab, _(u"Home"))
		self.repeatedUpdate = RepeatingTimer(180, self.update_all_buffers)
		self.repeatedUpdate.start()
		feed = buffers.feedBuffer(parent=self.window.tb, name="me_feed", composefunc="compose_status", session=self.session, endpoint="get", parent_endpoint="wall")
		self.buffers.append(feed)
		self.window.add_buffer(feed.tab, _(u"My wall"))
		audio = buffers.audioBuffer(parent=self.window.tb, name="me_audio", composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True)
		self.buffers.append(audio)
		self.window.add_buffer(audio.tab, _(u"My audios"))
		p_audio = buffers.audioBuffer(parent=self.window.tb, name="popular_audio", composefunc="compose_audio", session=self.session, endpoint="getPopular", parent_endpoint="audio", full_list=True)
		self.buffers.append(p_audio)
		self.window.add_buffer(p_audio.tab, _(u"Popular audios"))
		r_audio = buffers.audioBuffer(parent=self.window.tb, name="recommended_audio", composefunc="compose_audio", session=self.session, endpoint="getRecommendations", parent_endpoint="audio", full_list=True)
		self.buffers.append(r_audio)
		self.window.add_buffer(r_audio.tab, _(u"Recommendations"))

	def connect_events(self):
		pub.subscribe(self.in_post, "posted")
		pub.subscribe(self.download, "download-file")
		pub.subscribe(self.play_audio, "play-audio")
		pub.subscribe(self.play_audios, "play-audios")
		pub.subscribe(self.view_post, "open-post")
		widgetUtils.connect_event(self.window, widgetUtils.CLOSE_EVENT, self.exit)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.update_buffer, menuitem=self.window.update_buffer)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_for_updates, menuitem=self.window.check_for_updates)

	def disconnect_events(self):
		pub.unsubscribe(self.in_post, "posted")
		pub.unsubscribe(self.download, "download-file")
		pub.unsubscribe(self.play_audio, "play-audio")
		pub.unsubscribe(self.play_audios, "play-audios")
		pub.unsubscribe(self.view_post, "open-post")

	def login(self):
		self.window.change_status(_(u"Logging in VK"))
		self.session.login()
		self.window.change_status(_(u"Ready"))
		for i in self.buffers:
			if hasattr(i, "get_items"):
				self.window.change_status(_(u"Loading items for {0}").format(i.name,))
				i.get_items()
		self.window.change_status(_(u"Ready"))

	def in_post(self, buffer):
		buffer = self.search(buffer)
		buffer.get_items()
		buffer = self.search("home_timeline")
		buffer.get_items()

	def update_all_buffers(self):
		for i in self.buffers:
			if hasattr(i, "get_items"):
				i.get_items()
				print "executed for %s" % (i.name)

	def download(self, url, filename):
		call_threaded(utils.download_file, url, filename, self.window)

	def play_audio(self, audio_object):
		call_threaded(player.player.play, audio_object)

	def play_audios(self, audios):
		player.player.play_all(audios)

	def view_post(self, post_object, controller_):
		p = getattr(posts, controller_)(self.session, post_object)
		p.dialog.get_response()
		p.dialog.Destroy()

	def exit(self, *args, **kwargs):
		self.disconnect_events()
		self.window.Destroy()
#		wx.GetApp().ExitMainloop()

	def update_buffer(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_items()

	def check_for_updates(self, *args, **kwargs):
		update = updater.do_update()
		if update == False:
			commonMessages.no_update_available()
