# -*- coding: utf-8 -*-
import time
import os
import wx
import utils
import widgetUtils
import messages
import buffers
import configuration
import player
import posts
import profiles
import webbrowser
import logging
import longpollthread
import selector
from vk.exceptions import VkAuthError, VkAPIError
from pubsub import pub
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded
from mysc import localization
from sessionmanager import session
from wxUI import (mainWindow, commonMessages)
from wxUI.dialogs import search as searchDialogs
from wxUI.dialogs import timeline, creation
from update import updater

log = logging.getLogger("controller.main")

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
		log.debug("Starting main controller...")
		self.buffers = []
		player.setup()
		self.window = mainWindow.mainWindow()
		log.debug("Main window created")
		self.window.change_status(_(u"Ready"))
		self.session = session.sessions[session.sessions.keys()[0]]
		self.create_controls()
		self.window.Show()
		self.connect_events()
		call_threaded(updater.do_update)

	def create_controls(self):
		log.debug("Creating controls for the window...")
		posts_ = buffers.empty(parent=self.window.tb, name="posts")
		self.buffers.append(posts_)
		# Translators: Name for the posts tab in the tree view.
		self.window.add_buffer(posts_.tab, _(u"Posts"))
		home = buffers.baseBuffer(parent=self.window.tb, name="home_timeline", session=self.session, composefunc="compose_new", endpoint="newsfeed", count=self.session.settings["buffers"]["count_for_wall_buffers"])
		self.buffers.append(home)
		# Translators: Newsfeed's name in the tree view.
		self.window.insert_buffer(home.tab, _(u"Home"), self.window.search("posts"))
		self.repeatedUpdate = RepeatingTimer(180, self.update_all_buffers)
		self.repeatedUpdate.start()
		self.readMarker = RepeatingTimer(120, self.mark_as_read)
		self.readMarker.start()
		feed = buffers.feedBuffer(parent=self.window.tb, name="me_feed", composefunc="compose_status", session=self.session, endpoint="get", parent_endpoint="wall", extended=1, count=self.session.settings["buffers"]["count_for_wall_buffers"])
		self.buffers.append(feed)
		# Translators: Own user's wall name in the tree view.
		self.window.insert_buffer(feed.tab, _(u"My wall"), self.window.search("posts"))
		### Disabled audio stuff for now.
#		audios = buffers.empty(parent=self.window.tb, name="audios")
#		self.buffers.append(audios)
		# Translators: name for the music category in the tree view.
#		self.window.add_buffer(audios.tab, _(u"Music"))

#		audio = buffers.audioBuffer(parent=self.window.tb, name="me_audio", composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"])
#		self.buffers.append(audio)
#		self.window.insert_buffer(audio.tab, _(u"My audios"), self.window.search("audios"))
#		p_audio = buffers.audioBuffer(parent=self.window.tb, name="popular_audio", composefunc="compose_audio", session=self.session, endpoint="getPopular", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"])
#		self.buffers.append(p_audio)
#		self.window.insert_buffer(p_audio.tab, _(u"Populars"), self.window.search("audios"))
#		r_audio = buffers.audioBuffer(parent=self.window.tb, name="recommended_audio", composefunc="compose_audio", session=self.session, endpoint="getRecommendations", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"])
#		self.buffers.append(r_audio)
#		self.window.insert_buffer(r_audio.tab, _(u"Recommendations"), self.window.search("audios"))
#		albums = buffers.empty(parent=self.window.tb, name="albums")
#		self.buffers.append(albums)
#		self.window.insert_buffer(albums.tab, _(u"Albums"), self.window.search("audios"))
		videos = buffers.empty(parent=self.window.tb, name="videos")
		self.buffers.append(videos)
		# Translators: name for the videos category in the tree view.
		self.window.add_buffer(videos.tab, _(u"Video"))
		my_videos = buffers.videoBuffer(parent=self.window.tb, name="me_video", composefunc="compose_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"])
		self.buffers.append(my_videos)
		self.window.insert_buffer(my_videos.tab, _(u"My videos"), self.window.search("videos"))
		video_albums = buffers.empty(parent=self.window.tb, name="video_albums")
		self.buffers.append(video_albums)
		self.window.insert_buffer(video_albums.tab, _(u"Albums"), self.window.search("videos"))
		people = buffers.empty(parent=self.window.tb, name="people")
		self.buffers.append(people)
		self.window.add_buffer(people.tab, _(u"People"))
		friends = buffers.peopleBuffer(parent=self.window.tb, name="friends_", composefunc="compose_person", session=self.session, endpoint="get", parent_endpoint="friends", count=5000, fields="uid, first_name, last_name, last_seen")
		self.buffers.append(friends)
		self.window.insert_buffer(friends.tab, _(u"Friends"), self.window.search("people"))
		requests_ = buffers.empty(parent=self.window.tb, name="requests")
		self.buffers.append(requests_)
		self.window.insert_buffer(requests_.tab, _(u"Friendship requests"), self.window.search("people"))
		incoming_requests = buffers.requestsBuffer(parent=self.window.tb, name="friend_requests", composefunc="compose_person", session=self.session, count=1000)
		self.buffers.append(incoming_requests)
		self.window.insert_buffer(incoming_requests.tab, _(u"Pending requests"), self.window.search("requests"))
		outgoing_requests = buffers.requestsBuffer(parent=self.window.tb, name="friend_requests_sent", composefunc="compose_person", session=self.session, count=1000, out=1)
		self.buffers.append(outgoing_requests)
		self.window.insert_buffer(outgoing_requests.tab, _(u"I follow"), self.window.search("requests"))
		chats = buffers.empty(parent=self.window.tb, name="chats")
		self.buffers.append(chats)
		self.window.add_buffer(chats.tab, _(u"Chats"))
		timelines = buffers.empty(parent=self.window.tb, name="timelines")
		self.buffers.append(timelines)
		self.window.add_buffer(timelines.tab, _(u"Timelines"))
		self.window.realize()

	def connect_events(self):
		log.debug("Connecting events to responses...")
		pub.subscribe(self.in_post, "posted")
		pub.subscribe(self.download, "download-file")
		pub.subscribe(self.play_audio, "play-audio")
#		pub.subscribe(self.play_audios, "play-audios")
		pub.subscribe(self.view_post, "open-post")
		pub.subscribe(self.update_status_bar, "update-status-bar")
		pub.subscribe(self.chat_from_id, "new-chat")
		pub.subscribe(self.authorisation_failed, "authorisation-failed")
		pub.subscribe(self.user_profile, "user-profile")
		widgetUtils.connect_event(self.window, widgetUtils.CLOSE_EVENT, self.exit)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.update_buffer, menuitem=self.window.update_buffer)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_for_updates, menuitem=self.window.check_for_updates)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.window.about_dialog, menuitem=self.window.about)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.search_audios, menuitem=self.window.search_audios)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.search_videos, menuitem=self.window.search_videos)
		widgetUtils.connect_event(self.window, widgetUtils.MENU,self.remove_buffer, menuitem=self.window.remove_buffer_)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.get_more_items, menuitem=self.window.load_previous_items)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.changelog, menuitem=self.window.changelog)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.configuration, menuitem=self.window.settings_dialog)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.new_timeline, menuitem=self.window.timeline)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.create_audio_album, menuitem=self.window.audio_album)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.delete_audio_album, menuitem=self.window.delete_audio_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.create_video_album, menuitem=self.window.video_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.delete_video_album, menuitem=self.window.delete_video_album)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.check_documentation, menuitem=self.window.documentation)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_pause, menuitem=self.window.player_play)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_next, menuitem=self.window.player_next)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_previous, menuitem=self.window.player_previous)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_play_all, menuitem=self.window.player_play_all)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_stop, menuitem=self.window.player_stop)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_volume_down, menuitem=self.window.player_volume_down)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_volume_up, menuitem=self.window.player_volume_up)
#		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.menu_mute, menuitem=self.window.player_mute)
		pub.subscribe(self.get_chat, "order-sent-message")
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.view_my_profile, menuitem=self.window.view_profile)
		widgetUtils.connect_event(self.window, widgetUtils.MENU, self.view_my_profile_in_browser, menuitem=self.window.open_in_browser)
	def disconnect_events(self):
		log.debug("Disconnecting some events...")
		pub.unsubscribe(self.in_post, "posted")
#		pub.unsubscribe(self.download, "download-file")
#		pub.unsubscribe(self.play_audio, "play-audio")
		pub.unsubscribe(self.authorisation_failed, "authorisation-failed")
#		pub.unsubscribe(self.play_audios, "play-audios")
		pub.unsubscribe(self.view_post, "open-post")
		pub.unsubscribe(self.update_status_bar, "update-status-bar")

	def authorisation_failed(self):
		commonMessages.bad_authorisation()

	def login(self):
		self.window.change_status(_(u"Logging in VK"))
		self.session.login()
		self.window.change_status(_(u"Ready"))
		for i in self.buffers:
			if hasattr(i, "get_items"):
				# Translators: {0} will be replaced with the name of a buffer.
				self.window.change_status(_(u"Loading items for {0}").format(i.name,))
				i.get_items()
		self.window.change_status(_(u"Ready"))
		self.longpoll = longpollthread.worker(self.session)
		self.longpoll.start()
		self.status_setter = RepeatingTimer(900, self.set_online)
		self.status_setter.start()
		self.set_online()
		self.create_unread_messages()
		wx.CallAfter(self.get_audio_albums, self.session.user_id)
		wx.CallAfter(self.get_video_albums, self.session.user_id)

	def in_post(self, buffer):
		buffer = self.search(buffer)
		buffer.get_items()
		buffer = self.search("home_timeline")
		buffer.get_items()

	def update_all_buffers(self):
		log.debug("Updating buffers...")
		self.session.audio_albums = self.session.vk.client.audio.getAlbums(owner_id=self.session.user_id)["items"]
		for i in self.buffers:
			if hasattr(i, "get_items"):
				i.get_items()
				log.debug(u"Updated %s" % (i.name))

	def download(self, url, filename):
		log.debug(u"downloading %s URL to %s filename" % (url, filename,))
		call_threaded(utils.download_file, url, filename, self.window)

	def play_audio(self, audio_object):
		call_threaded(player.player.play, audio_object)

	def play_audios(self, audios):
		player.player.play_all(audios, shuffle=self.window.player_shuffle.IsChecked())

	def view_post(self, post_object, controller_):
		p = getattr(posts, controller_)(self.session, post_object)
		p.dialog.get_response()
		p.dialog.Destroy()

	def exit(self, *args, **kwargs):
		log.debug("Receibed an exit signal. closing...")
		self.disconnect_events()
		self.window.Destroy()
		wx.GetApp().ExitMainLoop()

	def update_buffer(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_items()

	def get_more_items(self, *args, **kwargs):
		b = self.get_current_buffer()
		b.get_more_items()

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
			# Translators: {0} will be replaced with the search term.
			self.window.insert_buffer(newbuff.tab, _(u"Search for {0}").format(q.decode("utf-8"),), self.window.search("audios"))

	def search_videos(self, *args, **kwargs):
		dlg = searchDialogs.searchVideoDialog()
		if dlg.get_response() == widgetUtils.OK:
			params = {}
			params["q"] = dlg.get("term").encode("utf-8")
			params["count"] = 200
			hd = dlg.get_checkable("hd")
			if hd != 0:
				params["hd"] = 1
			params["adult"] = dlg.get_checkable("safe_search")
			params["sort"] = dlg.get_sort_order()
			params["filters"] = "youtube, vimeo, short, long"
			newbuff = buffers.videoBuffer(parent=self.window.tb, name=u"{0}_videosearch".format(params["q"].decode("utf-8"),), session=self.session, composefunc="compose_video", parent_endpoint="video", endpoint="search", **params)
			self.buffers.append(newbuff)
			call_threaded(newbuff.get_items)
			# Translators: {0} will be replaced with the search term.
			self.window.insert_buffer(newbuff.tab, _(u"Search for {0}").format(params["q"].decode("utf-8"),), self.window.search("videos"))

	def update_status_bar(self, status):
		self.window.change_status(status)

	def remove_buffer(self, event, mandatory=False, *args, **kwargs):
		buffer = self.get_current_buffer()
		buff = self.window.search(buffer.name)
		answer = buffer.remove_buffer(mandatory)
		if answer == False:
			return
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer

	def changelog(self, *args, **kwargs):
		os.chdir("documentation")
		webbrowser.open("changelog.html")
		os.chdir("../")

	def configuration(self, *args, **kwargs):
		""" Opens the global settings dialogue."""
		d = configuration.configuration(self.session)
		if d.response == widgetUtils.OK:
			d.save_configuration()

	def new_timeline(self, *args, **kwargs):
		b = self.get_current_buffer()
		if not hasattr(b, "get_users"):
			b = self.search("home_timeline")
		d = []
		for i in self.session.db["users"]:
			d.append((i, self.session.get_user_name(i, "nom")))
		for i in self.session.db["groups"]:
			d.append((-i, self.session.get_user_name(-i)))
		a = timeline.timelineDialog([i[1] for i in d])
		if a.get_response() == widgetUtils.OK:
			user = a.get_user()
			buffertype = a.get_buffer_type()
			user_id = ""
			for i in d:
				if i[1] == user:
					user_id = i[0]
			if user_id == None:
				commonMessages.no_user_exist()
				return
			if buffertype == "audio":
				buffer = buffers.audioBuffer(parent=self.window.tb, name="{0}_audio".format(user_id,), composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"], owner_id=user_id)
				# Translators: {0} will be replaced with an user.
				name_ = _(u"{0}'s audios").format(self.session.get_user_name(user_id, "gen"),)
			elif buffertype == "wall":
				buffer = buffers.feedBuffer(parent=self.window.tb, name="{0}_feed".format(user_id,), composefunc="compose_status", session=self.session, endpoint="get", parent_endpoint="wall", extended=1, count=self.session.settings["buffers"]["count_for_wall_buffers"],  owner_id=user_id)
				# Translators: {0} will be replaced with an user.
				name_ = _(u"{0}'s wall posts").format(self.session.get_user_name(user_id, "gen"),)
			elif buffertype == "friends":
				buffer = buffers.peopleBuffer(parent=self.window.tb, name="friends_{0}".format(user_id,), composefunc="compose_person", session=self.session, endpoint="get", parent_endpoint="friends", count=5000, fields="uid, first_name, last_name, last_seen", user_id=user_id)
				# Translators: {0} will be replaced with an user.
				name_ = _(u"{0}'s friends").format(self.session.get_user_name(user_id, "friends"),)
			self.buffers.append(buffer)
			call_threaded(self.complete_buffer_creation, buffer=buffer, name_=name_, position=self.window.search("timelines"))

	def complete_buffer_creation(self, buffer, name_, position):
		answer = buffer.get_items()
		if answer is not True:
			self.buffers.remove(buffer)
			del buffer
			commonMessages.show_error_code(answer)
			return
		self.window.insert_buffer(buffer.tab, name_, position)

	def search_chat_buffer(self, user_id):
		for i in self.buffers:
			if "_messages" in i.name:
				if i.kwargs.has_key("user_id") and i.kwargs["user_id"] == user_id: return i
		return None

	def chat_from_id(self, user_id, setfocus=True):
		b = self.search_chat_buffer(user_id)
		if b != None:
			pos = self.window.search(b.name)
			if setfocus:
				self.window.change_buffer(pos)
				return b.tab.text.SetFocus()
			return
		buffer = buffers.chatBuffer(parent=self.window.tb, name="{0}_messages".format(user_id,), composefunc="compose_message", session=self.session, count=200,  user_id=user_id, rev=0)
		self.buffers.append(buffer)
		# Translators: {0} will be replaced with an user.
		self.window.insert_buffer(buffer.tab, _(u"Chat with {0}").format(self.session.get_user_name(user_id, "ins")), self.window.search("chats"))
		if setfocus:
			pos = self.window.search(buffer.name)
			self.window.change_buffer(pos)
		wx.CallAfter(buffer.get_items)
		if setfocus: buffer.tab.text.SetFocus()
		return True

	def get_chat(self, obj=None):
		""" Searches or creates a chat buffer with the id of the user that is sending or receiving a message.
			obj mysc.longpoll.event: an event wich defines some data from the vk's long poll server."""
		print obj
		# Set user_id to the id of the friend wich is receiving or sending the message.
		obj.user_id = obj.from_id
		buffer = self.search_chat_buffer(obj.user_id)
		if buffer == None:
			wx.CallAfter(self.chat_from_id, obj.user_id)
			self.session.soundplayer.play("chat.ogg")
			return
		# If the chat already exists, let's create a dictionary wich will contains data of the received message.
		message = {"id": obj.message_id, "user_id": obj.user_id, "date": obj.timestamp, "body": obj.text, "attachments": obj.attachments}
		# if attachments is true, let's request for the full message with attachments formatted in a better way.
		# Todo: code improvements. We shouldn't need to request the same message again just for these attachments.
		if len(message["attachments"]) != 0:
			message_ids = message["id"]
			results = self.session.vk.client.messages.getById(message_ids=message_ids)
			message = results["items"][0]
		# If outbox it's true, it means that message["from_id"] should be the current user. If not, the obj.user_id should be taken.
		if obj.message_flags.has_key("outbox") == True:
			message["from_id"] = self.session.user_id
		else:
			message["from_id"] = obj.from_id
		data = [message]
		# Let's add this to the buffer.
		# ToDo: Clean this code and test how is the database working with this set to True.
		num = self.session.order_buffer(buffer.name, data, True)
		buffer.insert(self.session.db[buffer.name]["items"][-1], False)
		self.session.soundplayer.play("chat.ogg")

	def set_online(self):
		try:
			r = self.session.vk.client.account.setOnline()
		except:
			log.error("Error in setting online for the current user")

	def create_unread_messages(self):
		try:
			log.debug("Getting possible unread messages.")
			msgs = self.session.vk.client.messages.getDialogs(count=200, unread=1)
		except VkAPIError as ex:
			if ex.code == 6:
				log.exception("Something went wrong when getting messages. Waiting a second to retry")
				time.sleep(2)
				return self.create_unread_messages()
		for i in msgs["items"]:
			wx.CallAfter(self.chat_from_id, i["message"]["user_id"], setfocus=False)

	def mark_as_read(self):
		ids = ""
		for i in self.buffers:
			if hasattr(i, "reads"):
				for z in i.reads:
					ids = ids+"%d," % (z,)
				i.reads = []
		if ids != "":
			response = self.session.vk.client.messages.markAsRead(message_ids=ids)

	def get_audio_albums(self, user_id=None):
		try:
			log.debug("Create audio albums...")
			albums = self.session.vk.client.audio.getAlbums(owner_id=user_id)
		except VkAPIError as ex:
			if ex.code == 6:
				log.exception("Something went wrong when getting albums. Waiting a second to retry")
				time.sleep(2)
				return self.get_audio_albums(user_id=user_id)
			elif ex.code == 10:
				return
		self.session.audio_albums = albums["items"]
		for i in albums["items"]:
			buffer = buffers.audioAlbum(parent=self.window.tb, name="{0}_audio_album".format(i["id"],), composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"], user_id=user_id, album_id=i["id"])
			buffer.can_get_items = False
			# Translators: {0} Will be replaced with an audio album's title.
			name_ = _(u"Album: {0}").format(i["title"],)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("albums"))
			buffer.get_items()
			# inserts a pause of 1 second here, so we'll avoid errors 6 in VK.
			time.sleep(0.3)

	def get_video_albums(self, user_id=None):
		try:
			log.debug("Create video  albums...")
			albums = self.session.vk.client.video.getAlbums(owner_id=user_id)
		except VkAPIError as ex:
			if ex.code == 6:
				log.exception("Something went wrong when getting albums. Waiting a second to retry")
				time.sleep(2)
				return self.get_audio_albums(user_id=user_id)
		self.session.video_albums = albums["items"]
		for i in albums["items"]:
			buffer = buffers.videoAlbum(parent=self.window.tb, name="{0}_video_album".format(i["id"],), composefunc="compose_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"], user_id=user_id, album_id=i["id"])
			buffer.can_get_items = False
			# Translators: {0} Will be replaced with a video  album's title.
			name_ = _(u"Album: {0}").format(i["title"],)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("video_albums"))
			buffer.get_items()
			# inserts a pause of 1 second here, so we'll avoid errors 6 in VK.
			time.sleep(0.3)

	def create_audio_album(self, *args, **kwargs):
		d = creation.audio_album()
		if d.get_response() == widgetUtils.OK and d.get("title") != "":
			response = self.session.vk.client.audio.addAlbum(title=d.get("title"))
			if response.has_key("album_id") == False: return
			album_id = response["album_id"]
			buffer = buffers.audioAlbum(parent=self.window.tb, name="{0}_audio_album".format(album_id,), composefunc="compose_audio", session=self.session, endpoint="get", parent_endpoint="audio", full_list=True, count=self.session.settings["buffers"]["count_for_audio_buffers"], user_id=self.session.user_id, album_id=album_id)
			buffer.can_get_items = False
			# Translators: {0} will be replaced with an audio album's title.
			name_ = _(u"Album: {0}").format(d.get("title"),)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("albums"))
			buffer.get_items()
			self.session.audio_albums = self.session.vk.client.audio.getAlbums(owner_id=self.session.user_id)["items"]

	def delete_audio_album(self, *args, **kwargs):
		answer = selector.album(_(u"Select the album you want to delete"), self.session)
		if answer.item == None:
			return
		response = commonMessages.delete_audio_album()
		if response != widgetUtils.YES: return
		removal = self.session.vk.client.audio.deleteAlbum(album_id=answer.item)
		buffer = self.search("{0}_audio_album".format(answer.item,))
		buff = self.window.search(buffer.name)
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer
		self.session.audio_albums = self.session.vk.client.audio.getAlbums(owner_id=self.session.user_id)["items"]

	def create_video_album(self, *args, **kwargs):
		d = creation.audio_album()
		if d.get_response() == widgetUtils.OK and d.get("title") != "":
			response = self.session.vk.client.video.addAlbum(title=d.get("title"))
			if response.has_key("album_id") == False: return
			album_id = response["album_id"]
			buffer = buffers.videoAlbum(parent=self.window.tb, name="{0}_video_album".format(album_id,), composefunc="compose_video", session=self.session, endpoint="get", parent_endpoint="video", count=self.session.settings["buffers"]["count_for_video_buffers"], user_id=self.session.user_id, album_id=album_id)
			buffer.can_get_items = False
			# Translators: {0} will be replaced with a video  album's title.
			name_ = _(u"Album: {0}").format(d.get("title"),)
			self.buffers.append(buffer)
			self.window.insert_buffer(buffer.tab, name_, self.window.search("video_albums"))
			buffer.get_items()
			self.session.video_albums = self.session.vk.client.video.getAlbums(owner_id=self.session.user_id)["items"]

	def delete_video_album(self, *args, **kwargs):
		answer = selector.album(_(u"Select the album you want to delete"), self.session, "video_albums")
		if answer.item == None:
			return
		response = commonMessages.delete_audio_album()
		if response != widgetUtils.YES: return
		removal = self.session.vk.client.video.deleteAlbum(album_id=answer.item)
		buffer = self.search("{0}_video_album".format(answer.item,))
		buff = self.window.search(buffer.name)
		self.window.remove_buffer(buff)
		self.buffers.remove(buffer)
		del buffer
		self.session.video_albums = self.session.vk.client.video.getAlbums(owner_id=self.session.user_id)["items"]

	def check_documentation(self, *args, **kwargs):
		lang = localization.get("documentation")
		os.chdir("documentation/%s" % (lang,))
		webbrowser.open("manual.html")
		os.chdir("../../")

	def menu_play_pause(self, *args, **kwargs):
		if player.player.check_is_playing() != False:
			return player.player.pause()
		b = self.get_current_buffer()
		if hasattr(b, "play_next"):
			b.play_audio()
		else:
			b = self.search("me_audio")
			b.play_audio()

	def menu_play_next(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_next"):
			b.play_next()
		else:
			self.search("me_audio").play_next()

	def menu_play_previous(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_previous"):
			b.play_previous()
		else:
			self.search("me_audio").play_previous()

	def menu_play_all(self, *args, **kwargs):
		b = self.get_current_buffer()
		if hasattr(b, "play_all"):
			b.play_all()
		else:
			self.search("me_audio").play_all()

	def menu_stop(self, *args, **kwargs):
		player.player.stop()

	def menu_volume_down(self, *args, **kwargs):
		player.player.volume = player.player.volume-5

	def menu_volume_up(self, *args, **kwargs):
		player.player.volume = player.player.volume+5

	def menu_mute(self, *args, **kwargs):
		player.player.volume = 0

	def user_profile(self, person):
		p = profiles.userProfile(self.session, person)

	def view_my_profile(self, *args, **kwargs):
		self.user_profile(self.session.user_id)

	def view_my_profile_in_browser(self, *args, **kwargs):
		webbrowser.open_new_tab("https://vk.com/id{id}".format(id=self.session.user_id,))