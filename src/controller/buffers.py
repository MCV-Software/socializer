# -*- coding: utf-8 -*-
import languageHandler
import arrow
import wx
import widgetUtils
import messages
import utils
import posts
import player
import output
import logging
import selector
from wxUI.tabs import home
from pubsub import pub
from sessionmanager import session
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus
from vk import upload
from vk.exceptions import VkAPIMethodError

log = logging.getLogger("controller.buffers")

class baseBuffer(object):
	""" a basic representation of a buffer. Other buffers should be derived from this class"""

	def get_post(self):
		return self.session.db[self.name]["items"][self.tab.list.get_selected()]

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
		self.user_key = "source_id"
		self.post_key = "post_id"
		self.can_get_items = True

	def create_tab(self, parent):
		""" Creates the Wx panel."""
		self.tab = home.homeTab(parent)

	def insert(self, item, reversed=False):
		""" Add a new item to the list. Uses session.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
		item_ = getattr(session, self.compose_function)(item, self.session)
		self.tab.list.insert_item(reversed, *item_)

	def get_items(self, show_nextpage=False):
		""" Retrieves items from the VK API. This function is called repeatedly by the main controller and users could call it implicitly as well with the update buffer option.
		show_nextpage boolean: If it's true, it will try to load previous results.
		"""
		if self.can_get_items == False: return
		retrieved = True # Control variable for handling unauthorised/connection errors.
		try:
			num = getattr(self.session, "get_newsfeed")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		except VkAPIMethodError as err:
			print(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
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
		return retrieved

	def get_more_items(self):
		self.get_items(show_nextpage=True)

	def post(self, *args, **kwargs):
		p = messages.post(title=_(u"Write your post"), caption="", text="")
		if p.message.get_response() == widgetUtils.OK:
			call_threaded(self.do_last, p=p)

	def do_last(self, p):
		msg = p.message.get_text().encode("utf-8")
		privacy_opts = p.get_privacy_options()
		attachments = ""
		if hasattr(p, "attachments"):
			attachments = self.upload_attachments(p.attachments)
		urls = utils.find_urls_in_text(msg)
		if len(urls) != 0:
			if len(attachments) == 0: attachments = urls[0]
			else: attachments += urls[0]
			msg = msg.replace(urls[0], "")
		self.session.post_wall_status(message=msg, friends_only=privacy_opts, attachments=attachments)
		pub.sendMessage("posted", buffer=self.name)
		p.message.Destroy()

	def upload_attachments(self, attachments):
		# To do: Check the caption and description fields for this kind of attachments.
		local_attachments = ""
		uploader = upload.VkUpload(self.session.vk.client)
		for i in attachments:
			if i["type"] == "photo":
				photos = i["file"]
				description = i["description"]
				r = uploader.photo_wall(photos, caption=description)
				id = r[0]["id"]
				owner_id = r[0]["owner_id"]
#				self.session.vk.client.photos.edit(photo_id=id, owner_id=owner_id, caption=description)
				local_attachments += "photo{0}_{1},".format(owner_id, id)
		return local_attachments

	def connect_events(self):
		widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
		widgetUtils.connect_event(self.tab.list.list, widgetUtils.KEYPRESS, self.get_event)
		widgetUtils.connect_event(self.tab.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
		widgetUtils.connect_event(self.tab.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)
		self.tab.set_focus_function(self.onFocus)

	def show_menu(self, ev, pos=0, *args, **kwargs):
		if self.tab.list.get_count() == 0: return
		menu = self.get_menu()
		if pos != 0:
			self.tab.PopupMenu(menu, pos)
		else:
			self.tab.PopupMenu(menu, ev.GetPosition())

	def show_menu_by_key(self, ev):
		if self.tab.list.get_count() == 0:
			return
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			self.show_menu(widgetUtils.MENU, pos=self.tab.list.list.GetPosition())

	def get_menu(self):
		m = menus.postMenu()
		p = self.get_post()
		if p.has_key("likes") == False:
			m.like.Enable(False)
		elif p["likes"]["user_likes"] == 1:
			m.like.Enable(False)
			m.dislike.Enable(True)
		if p.has_key("comments") == False:
			m.comment.Enable(False)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_like, menuitem=m.like)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_dislike, menuitem=m.dislike)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_comment, menuitem=m.comment)
		return m

	def do_like(self, *args, **kwargs):
		post = self.get_post()
		user = post[self.user_key]
		id = post[self.post_key]
		if post.has_key("type"):
			type_ = post["type"]
		else:
			type_ = "post"
		l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 1
		# Translators: This will be used when user presses like.
		output.speak(_(u"You liked this"))

	def do_dislike(self, *args, **kwargs):
		post = self.get_post()
		user = post[self.user_key]
		id = post[self.post_key]
		if post.has_key("type"):
			type_ = post["type"]
		else:
			type_ = "post"
		l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 2
		# Translators: This will be user in 'dislike'
		output.speak(_(u"You don't like this"))

	def do_comment(self, *args, **kwargs):
		comment = messages.comment(title=_(u"Add a comment"), caption="", text="")
		if comment.message.get_response() == widgetUtils.OK:
			msg = comment.message.get_text().encode("utf-8")
			post = self.get_post()
			try:
				user = post[self.user_key]
				id = post[self.post_key]
				self.session.vk.client.wall.addComment(owner_id=user, post_id=id, text=msg)
				output.speak(_(u"You've posted a comment"))
			except Exception as msg:
				print msg

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
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		post = self.session.db[self.name]["items"][selected]
		if post.has_key("type") and post["type"] == "audio":
			pub.sendMessage("play-audio", audio_object=post["audio"]["items"][0])
			return True

	def open_post(self, *args, **kwargs):
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

	def remove_buffer(self, mandatory): return False

	def get_users(self):
		post = self.session.db[self.name]["items"][self.tab.list.get_selected()]
		if post.has_key("type") == False:
			return [post["from_id"]]
		else:
			return [post["source_id"]]

	def onFocus(self, *args,**kwargs):
		""" Function executed when the item in a list is selected.
		For this buffer it updates the date of posts in the list."""
		post = self.session.db[self.name]["items"][self.tab.list.get_selected()]
		original_date = arrow.get(post["date"])
		created_at = original_date.humanize(locale=languageHandler.getLanguage())
		self.tab.list.list.SetStringItem(self.tab.list.get_selected(), 2, created_at)


class feedBuffer(baseBuffer):

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True
		try:
			num = getattr(self.session, "get_page")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
			print num
		except VkAPIMethodError as err:
			print(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		return retrieved

	def remove_buffer(self, mandatory=False):
		if "me_feed" == self.name:
			output.speak(_(u"This buffer can't be deleted"))
			return False
		else:
			if mandatory == False:
				dlg = commonMessages.remove_buffer()
			else:
				dlg = widgetUtils.YES
			if dlg == widgetUtils.YES:
				self.session.db.pop(self.name)
				return True
			else:
				return False

	def __init__(self, *args, **kwargs):
		super(feedBuffer, self).__init__(*args, **kwargs)
		self.user_key = "from_id"
		self.post_key = "id"

class audioBuffer(feedBuffer):
	def create_tab(self, parent):
		self.tab = home.audioTab(parent)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		widgetUtils.connect_event(self.tab.play_all, widgetUtils.BUTTON_PRESSED, self.play_all)
		super(audioBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		pub.sendMessage("play-audio", audio_object=self.session.db[self.name]["items"][selected])
		return True

	def play_next(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected < 0 or selected == self.tab.list.get_count()-1:
			selected = 0
		if self.tab.list.get_count() <= selected+1:
			newpos = 0
		else:
			newpos = selected+1
		self.tab.list.select_item(newpos)
		self.play_audio()

	def play_previous(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected <= 0:
			selected = self.tab.list.get_count()
		newpos = selected-1
		self.tab.list.select_item(newpos)
		self.play_audio()

	def open_post(self, *args, **kwargs):
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
		return True

	def remove_buffer(self, mandatory=False):
		if "me_audio" == self.name or "popular_audio" == self.name or "recommended_audio" == self.name:
			output.speak(_(u"This buffer can't be deleted"))
			return False
		else:
			if mandatory == False:
				dlg = commonMessages.remove_buffer()
			else:
				dlg = widgetUtils.YES
			if dlg == widgetUtils.YES:
				self.session.db.pop(self.name)
				return True
			else:
				return False

	def get_more_items(self, *args, **kwargs):
		# Translators: Some buffers can't use the get previous item feature due to API limitations.
		output.speak(_(u"This buffer doesn't support getting more items."))

	def onFocus(self, *args, **kwargs):
		pass

	def add_to_library(self, *args, **kwargs):
		post = self.get_post()
		args = {}
		args["audio_id"] = post["id"]
		if post.has_key("album_id"):
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			output.speak(_(u"Audio added to your library"))

	def remove_from_library(self, *args, **kwargs):
		post = self.get_post()
		args = {}
		args["audio_id"] = post["id"]
		args["owner_id"] = self.session.user_id
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			output.speak(_(u"Removed audio from library"))
			self.tab.list.remove_item(self.tab.list.get_selected())

	def move_to_album(self, *args, **kwargs):
		album = selector.audioAlbum(_(u"Select the album where you want to move this song"), self.session)
		if album.item == None: return
		id = self.get_post()["id"]
		response = self.session.vk.client.audio.moveToAlbum(album_id=album.item, audio_ids=id)
		if response == 1:
		# Translators: Used when the user has moved an audio to an album.
			output.speak(_(u"Moved"))

	def get_menu(self):
		p = self.get_post()
		m = menus.audioMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.play_audio, menuitem=m.play)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_(u"&Remove from library"))
			widgetUtils.connect_event(m, widgetUtils.MENU, self.remove_from_library, menuitem=m.library)
		else:
			widgetUtils.connect_event(m, widgetUtils.MENU, self.add_to_library, menuitem=m.library)
		return m

class audioAlbum(audioBuffer):

	def create_tab(self, parent):
		self.tab = home.audioAlbumTab(parent)
		self.tab.play.Enable(False)
		self.tab.play_all.Enable(False)

	def connect_events(self):
		super(audioAlbum, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_album)

	def load_album(self, *args, **kwargs):
		output.speak(_(u"Loading album..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)
		self.tab.play.Enable(True)
		self.tab.play_all.Enable(True)

class empty(object):

	def __init__(self, name=None, parent=None, *args, **kwargs):
		self.tab = home.empty(parent=parent, name=name)
		self.name = name

	def get_items(self, *args, **kwargs):
		pass

	def get_more_items(self, *args, **kwargs):
		output.speak(_(u"This buffer doesn't support getting more items."))

	def remove_buffer(self, mandatory=False): return False

class chatBuffer(baseBuffer):

	def onFocus(self, *args, **kwargs):
		msg = self.session.db[self.name]["items"][-1]
		if msg.has_key("read_state") and msg["read_state"] == 0 and msg["id"] not in self.reads:
			self.reads.append(msg["id"])
			self.session.db[self.name]["items"][-1]["read_state"] = 1

	def create_tab(self, parent):
		self.tab = home.chatTab(parent)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.send, widgetUtils.BUTTON_PRESSED, self.send_chat_to_user)
		self.tab.set_focus_function(self.onFocus)

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True # Control variable for handling unauthorised/connection errors.
		try:
			num = getattr(self.session, "get_messages")(name=self.name, *self.args, **self.kwargs)
		except VkAPIMethodError as err:
			print(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
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
		return retrieved

	def send_chat_to_user(self, *args, **kwargs):
		text = self.tab.text.GetValue()
		if text == "": return
		response = self.session.vk.client.messages.send(user_id=self.kwargs["user_id"], message=text)

	def __init__(self, *args, **kwargs):
		super(chatBuffer, self).__init__(*args, **kwargs)
		self.reads = []

class peopleBuffer(feedBuffer):

	def create_tab(self, parent):
		self.tab = home.peopleTab(parent)

	def connect_events(self):
		super(peopleBuffer, self).connect_events()
		widgetUtils.connect_event(self.tab.new_chat, widgetUtils.BUTTON_PRESSED, self.new_chat)

	def new_chat(self, *args, **kwargs):
		user_id = self.session.db[self.name]["items"][self.tab.list.get_selected()]["id"]
		pub.sendMessage("new-chat", user_id=user_id)

	def onFocus(self, *args, **kwargs):
		post = self.session.db[self.name]["items"][self.tab.list.get_selected()]
		if post.has_key("last_seen") == False: return
		original_date = arrow.get(post["last_seen"]["time"])
		created_at = original_date.humanize(locale=languageHandler.getLanguage())
		self.tab.list.list.SetStringItem(self.tab.list.get_selected(), 1, created_at)

	def open_timeline(self, *args, **kwargs):
		pass

	def get_menu(self, *args, **kwargs):
		m = menus.peopleMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.new_chat, menuitem=m.message)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_timeline, menuitem=m.timeline)
		return m

	def open_post(self, *args, **kwargs): pass

	def play_audio(self, *args, **kwargs): return False

	def pause_audio(self, *args, **kwargs): pass

class requestsBuffer(peopleBuffer):

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True
		try:
			ids = self.session.vk.client.friends.getRequests(*self.args, **self.kwargs)
		except VkAPIMethodError as err:
			print(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		num = self.session.get_page(name=self.name, show_nextpage=show_nextpage, endpoint="get", parent_endpoint="users", count=1000, user_ids=", ".join([str(i) for i in ids["items"]]), fields="uid, first_name, last_name, last_seen")
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				print "inserting a value"
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		return retrieved
