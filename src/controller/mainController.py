# -*- coding: utf-8 -*-
import wx
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
from wxUI.dialogs import search as searchDialogs
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
		posts_ = buffers.empty(parent=self.window.tb, name="posts")
		self.buffers.append(posts_)
		self.window.add_buffer(posts_.tab, _(u"Posts"))
		home = buffers.baseBuffer(parent=self.window.tb, name="home_timeline", session=self.session, composefunc="compose_new", endpoint="newsfeed")
		self.buffers.append(home)
		self.window.insert_buffer(home.tab, _(u"Home"), self.window.search("posts"))
		self.repeatedUpdate = RepeatingTimer(180, self.update_all_buffers)
		self.repeatedUpdate.start()
		feed = buffers.feedBuffer(parent=self.window.tb, name="me_feed", composefunc="compose_status", session=self.session, endpoint="get", parent_endpoint="wall", extended=1)
		self.buffers.append(feed)
		self.window.insert_buffer(feed.tab, _(u"My wall"), self.window.search("posts"))
		audios = buffers.empty(parent=self.window.tb, name="audios")
		self.buffers.append(audios)
		self.window.add_buffer(audios.tab, _(u"Music"))
		audio = buffers.audioBuffer(parent=self.window.tb, name="me_audio", composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True)
		self.buffers.append(audio)
		self.window.insert_buffer(audio.tab, _(u"My audios"), self.window.search("audios"))
		p_audio = buffers.audioBuffer(parent=self.window.tb, name="popular_audio", composefunc="compose_audio", session=self.session, endpoint="getPopular", parent_endpoint="audio", full_list=True)
		self.buffers.append(p_audio)
		self.window.insert_buffer(p_audio.tab, _(u"Populars"), self.window.search("audios"))
		r_audio = buffers.audioBuffer(parent=self.window.tb, name="recommended_audio", composefunc="compose_audio", session=self.session, endpoint="getRecommendations", parent_endpoint="audio", full_list=True)
		self.buffers.append(r_audio)
		self.window.insert_buffer(r_audio.tab, _(u"Recommendations"), self.window.search("audios"))

	def connect_events(self):
		pub.subscribe(self.in_post, "posted")
		pub.subscribe(self.download, "download-file")
		pub.subscribe(self.play_audio, "play-audio")
		pub.subscribe(self.play_audios, "play-audios")
		pub.subscribe(self.view_post, "open-post")
		pub.subscribe(self.update_status_bar, "update-status-bar")
		widgetUtils.connect_event(self.window, widgetUtils.CLOSE_EVENT, self.exit)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.update_buffer, menuitem=self.window.update_buffer)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_for_updates, menuitem=self.window.check_for_updates)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.window.about_dialog, menuitem=self.window.about)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.search_audios, menuitem=self.window.search_audios)
		widgetUtils.connect_event(self.window, widgetUtils.MENU,self.remove_buffer, menuitem=self.window.remove_buffer_)

	def disconnect_events(self):
		pub.unsubscribe(self.in_post, "posted")
		pub.unsubscribe(self.download, "download-file")
		pub.unsubscribe(self.play_audio, "play-audio")
		pub.unsubscribe(self.play_audios, "play-audios")
		pub.unsubscribe(self.view_post, "open-post")
		pub.unsubscribe(self.update_status_bar, "update-status-bar")

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
#		print post_object
		p = getattr(posts, controller_)(self.session, post_object)
		p.dialog.get_response()
		p.dialog.Destroy()

	def exit(self, *args, **kwargs):
		self.disconnect_events()
		self.window.Destroy()
		wx.GetApp().ExitMainLoop()

	def update_buffer(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_items()

	def check_for_updates(self, *args, **kwargs):
		update = updater.do_update()
		if update == False:
			commonMessages.no_update_available()

	def search_audios(self, *args, **kwargs):
		dlg = searchDialogs.searchAudioDialog()
		if dlg.get_response() == widgetUtils.OK:
			q = dlg.get("term").encode("utf-8")
			count = 300
			auto_complete = dlg.get_checkable("auto_complete")
			lyrics = dlg.get_checkable("lyrics")
			performer_only = dlg.get_checkable("artist_only")
			sort = dlg.get_sort_order()
			newbuff = buffers.audioBuffer(parent=self.window.tb, name=u"{0}_audiosearch".format(q.decode("utf-8"),), session=self.session, composefunc="compose_audio", parent_endpoint="audio", endpoint="search", q=q, count=count, auto_complete=auto_complete, lyrics=lyrics, performer_only=performer_only, sort=sort)
			self.buffers.append(newbuff)
			call_threaded(newbuff.get_items)
			self.window.insert_buffer(newbuff.tab, _(u"Search for {0}").format(q.decode("utf-8"),), self.window.search("audios"))

	def update_status_bar(self, status):
		self.window.change_status(status)

	def remove_buffer(self, *args, **kwargs):
		buffer = self.get_current_buffer()
		buff = self.window.search(buffer.name)
		answer = buffer.remove_buffer()
		if answer == False:
			return
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer