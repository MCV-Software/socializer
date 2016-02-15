# -*- coding: utf-8 -*-
import widgetUtils
import messages
from wxUI import (mainWindow)
import buffers
from pubsub import pub
from mysc.repeating_timer import RepeatingTimer
from sessionmanager import session

class Controller(object):

	def search(self, tab_name):
		for i in xrange(0, len(self.buffers)):
			if self.buffers[i].name == tab_name:
				return self.buffers[i]
		return False

	def __init__(self):
		super(Controller, self).__init__()
		self.buffers = []
		self.window = mainWindow.mainWindow()
		self.window.change_status(_(u"Ready"))
		self.session = session.sessions[session.sessions.keys()[0]]
#		self.session.authorise()
		self.create_controls()
		self.window.Show()

	def create_controls(self):
		home = buffers.baseBuffer(parent=self.window.tb, name="home_timeline", session=self.session, composefunc="compose_new", endpoint="newsfeed", identifier="id")
		self.buffers.append(home)
		self.window.add_buffer(home.tab, _(u"Home"))
		self.repeatedUpdate = RepeatingTimer(180, self.update_all_buffers)
		self.repeatedUpdate.start()

		feed = buffers.feedBuffer(parent=self.window.tb, name="me_feed", composefunc="compose_status", session=self.session, endpoint="get", parent_endpoint="wall", identifier="id")
		self.buffers.append(feed)
		self.window.add_buffer(feed.tab, _(u"My wall"))
		audio = buffers.audioBuffer(parent=self.window.tb, name="me_audio", composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, identifier="aid")
		self.buffers.append(audio)
		self.window.add_buffer(audio.tab, _(u"My audios"))
		pub.subscribe(self.in_post, "posted")

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