# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belongs to a category (wall posts, messages, persons...)"""
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
import webbrowser
import posts
import attach
from wxUI.tabs import home
from pubsub import pub
from sessionmanager import session
from mysc.thread_utils import call_threaded
from mysc import upload
from wxUI import commonMessages, menus
from vk.exceptions import VkAPIError
from utils import add_attachment

log = logging.getLogger("controller.buffers")

class baseBuffer(object):
	""" a basic representation of a buffer. Other buffers should be derived from this class"""

	def get_post(self):
		""" Returns the currently focused post."""
		return self.session.db[self.name]["items"][self.tab.list.get_selected()]

	def __init__(self, parent=None, name="", session=None, composefunc=None, *args, **kwargs):
		""" Constructor:
		parent wx.Treebook: parent for the buffer panel,
		name str: Name for saving this buffer's data in the local storage variable,
		session sessionmanager.session.vkSession: Session for performing operations in the Vk API. This session should be logged in when this class is instanciated.
		composefunc str: This function will be called for composing the result which will be put in the listCtrl. Composefunc should existss in the sessionmanager.session module.
		args and kwargs will be passed to get_items() without any filtering. Be careful there."""
		super(baseBuffer, self).__init__()
		self.args = args
		self.kwargs = kwargs
		# Create GUI associated to this buffer.
		self.create_tab(parent)
		# Add name to the new control so we could look for it when needed.
		self.tab.name = name
		self.session = session
		self.compose_function = composefunc
		 #Update_function will be called every 3 minutes and it should be able to
		# Get all new items in the buffer and sort them properly in the CtrlList.
		# ToDo: Shall we allow dinamically set for update_function?
		self.update_function = "get_page"
		self.name = name
		# Bind local events (they will respond to events happened in the buffer).
		self.connect_events()
		# source_key and post_key will point to the keys for sender and posts in VK API objects.
		# They can be changed in the future for other item types in different buffers.
		self.user_key = "source_id"
		self.post_key = "post_id"
		# When set to False, update_function won't be executed here.
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
		except VkAPIError as err:
			log.error(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
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
		""" Returns previous items in the buffer."""
		self.get_items(show_nextpage=True)

	def post(self, *args, **kwargs):
		""" Create a post in the current user's wall.
		This process is handled in two parts. This is the first part, where the GUI is created and user can send the post.
		During the second part (threaded), the post will be sent to the API."""
		p = messages.post(session=self.session, title=_(u"Write your post"), caption="", text="")
		if p.message.get_response() == widgetUtils.OK:
			call_threaded(self.do_last, p=p)

	def do_last(self, p):
		""" Second part of post function. Here everything is going to be sent to the API"""
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
		""" Upload attachments to VK before posting them.
		Returns attachments formatted as string, as required by VK API.
		Currently this function only supports photos."""
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
		""" Bind all events to this buffer"""
		widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
		widgetUtils.connect_event(self.tab.list.list, widgetUtils.KEYPRESS, self.get_event)
		widgetUtils.connect_event(self.tab.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
		widgetUtils.connect_event(self.tab.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)
		self.tab.set_focus_function(self.onFocus)

	def show_menu(self, ev, pos=0, *args, **kwargs):
		""" Show contextual menu when pressing menu key or right mouse click in a list item."""
		if self.tab.list.get_count() == 0: return
		menu = self.get_menu()
		if pos != 0:
			self.tab.PopupMenu(menu, pos)
		else:
			self.tab.PopupMenu(menu, ev.GetPosition())

	def show_menu_by_key(self, ev):
		""" Show contextual menu when menu key is pressed"""
		if self.tab.list.get_count() == 0:
			return
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			self.show_menu(widgetUtils.MENU, pos=self.tab.list.list.GetPosition())

	def get_menu(self):
		""" Returns contextual menu options. They will change according to the focused item"""
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
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
		return m

	def do_like(self, *args, **kwargs):
		""" Set like in the currently focused post."""
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
		""" Set dislike (undo like) in the currently focused post."""
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
		""" Make a comment into the currently focused post."""
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
				log.error(msg)

	def get_event(self, ev):
		""" Parses keyboard input in the ListCtrl and executes the event associated with user keypresses."""
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
		""" Decreases player volume by 5%"""
		player.player.volume = player.player.volume-5

	def volume_up(self):
		""" Increases player volume by 5%"""
		player.player.volume = player.player.volume+5

	def play_audio(self, *args, **kwargs):
		""" Play audio in currently focused buffer, if possible."""
		post = self.get_post()
		if post.has_key("type") and post["type"] == "audio":
			pub.sendMessage("play-audio", audio_object=post["audio"]["items"][0])
			return True

	def open_person_profile(self, *args, **kwargs):
		""" Views someone's user profile."""
		selected = self.get_post()
		# Check all possible keys for an user object in VK API.
		keys = ["from_id", "source_id", "id"]
		for i in keys:
			if selected.has_key(i):
				pub.sendMessage("user-profile", person=selected[i])

	def open_post(self, *args, **kwargs):
		""" Opens the currently focused post."""
		post = self.get_post()
		if post.has_key("type") and post["type"] == "audio":
			a = posts.audio(self.session, post["audio"]["items"])
			a.dialog.get_response()
			a.dialog.Destroy()
		elif post.has_key("type") and post["type"] == "friend":
			pub.sendMessage("open-post", post_object=post, controller_="friendship")
		else:
			pub.sendMessage("open-post", post_object=post, controller_="postController")

	def pause_audio(self, *args, **kwargs):
		""" pauses audio playback."""
		player.player.pause()

	def remove_buffer(self, mandatory):
		""" Function for removing a buffer. Returns True if removal is successful, False otherwise"""
		return False

	def get_users(self):
		""" Returns source user in the post."""
		post = self.get_post()
		if post.has_key("type") == False:
			return [post["from_id"]]
		else:
			return [post["source_id"]]

	def onFocus(self, *args,**kwargs):
		""" Function executed when the item in a list is selected.
		For this buffer it updates the date of posts in the list."""
		post = self.get_post()
		original_date = arrow.get(post["date"])
		created_at = original_date.humanize(locale=languageHandler.getLanguage())
		self.tab.list.list.SetItem(self.tab.list.get_selected(), 2, created_at)

class feedBuffer(baseBuffer):
	""" This buffer represents an user's wall. It may be used either for the current user or someone else."""

	def get_items(self, show_nextpage=False):
		""" Update buffer with newest items or get older items in the buffer."""
		if self.can_get_items == False: return
		retrieved = True
		try:
			num = getattr(self.session, "get_page")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		except VkAPIMethodError as err:
			log.error(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		return retrieved

	def remove_buffer(self, mandatory=False):
		""" Remove buffer if the current buffer is not the logged user's wall."""
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
	""" this buffer was supposed to be used with audio elements
	but is deprecated as VK removed its audio support for third party apps."""

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
		album = selector.album(_(u"Select the album where you want to move this song"), self.session)
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
	""" this buffer was supposed to be used with audio albums
	but is deprecated as VK removed its audio support for third party apps."""

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

class videoBuffer(feedBuffer):
	""" This buffer represents video elements, and it can be used for showing videos for the logged user or someone else."""

	def create_tab(self, parent):
		self.tab = home.videoTab(parent)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		super(videoBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		""" Due to inheritance this method should be called play_audio, but play the currently focused video.
		Opens a webbrowser pointing to the video's URL."""
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		output.speak(_(u"Opening video in webbrowser..."))
		webbrowser.open_new_tab(self.session.db[self.name]["items"][selected]["player"])
		return True

	def open_post(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		audios = [self.session.db[self.name]["items"][selected]]
		a = posts.audio(self.session, audios)
		a.dialog.get_response()
		a.dialog.Destroy()

	def remove_buffer(self, mandatory=False):
		if "me_video" == self.name:
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
		args["video_id"] = post["id"]
		if post.has_key("album_id"):
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		video = self.session.vk.client.video.add(**args)
		if video != None and int(video) > 21:
			output.speak(_(u"Video added to your library"))

	def remove_from_library(self, *args, **kwargs):
		post = self.get_post()
		args = {}
		args["video_id"] = post["id"]
		args["owner_id"] = self.session.user_id
		result = self.session.vk.client.video.delete(**args)
		if int(result) == 1:
			output.speak(_(u"Removed video from library"))
			self.tab.list.remove_item(self.tab.list.get_selected())

	def move_to_album(self, *args, **kwargs):
		album = selector.album(_(u"Select the album where you want to move this video"), self.session, "video_albums")
		if album.item == None: return
		id = self.get_post()["id"]
		response = self.session.vk.client.video.addToAlbum(album_ids=album.item, video_id=id, target_id=self.session.user_id, owner_id=self.get_post()["owner_id"])
		if response == 1:
		# Translators: Used when the user has moved an video  to an album.
			output.speak(_(u"Moved"))

	def get_menu(self):
		""" We'll use the same menu that is used for audio items, as the options are exactly the same"""
		p = self.get_post()
		m = menus.audioMenu()
#		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
#		widgetUtils.connect_event(m, widgetUtils.MENU, self.play_audio, menuitem=m.play)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_(u"&Remove from library"))
			widgetUtils.connect_event(m, widgetUtils.MENU, self.remove_from_library, menuitem=m.library)
		else:
			widgetUtils.connect_event(m, widgetUtils.MENU, self.add_to_library, menuitem=m.library)
		return m

class videoAlbum(videoBuffer):

	def create_tab(self, parent):
		self.tab = home.videoAlbumTab(parent)
		self.tab.play.Enable(False)

	def connect_events(self):
		super(videoAlbum, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_album)

	def load_album(self, *args, **kwargs):
		output.speak(_(u"Loading album..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)
		self.tab.play.Enable(True)

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
		msg = self.get_post()
		if msg.has_key("attachments") and len(msg["attachments"]) > 0:
			self.tab.attachments.list.Enable(True)
			self.attachments = list()
			self.parse_attachments(msg)
		else:
			self.tab.attachments.list.Enable(False)
			self.tab.attachments.clear()

	def create_tab(self, parent):
		self.tab = home.chatTab(parent)
		self.attachments = list()

	def connect_events(self):
		widgetUtils.connect_event(self.tab.send, widgetUtils.BUTTON_PRESSED, self.send_chat_to_user)
		widgetUtils.connect_event(self.tab.attachment, widgetUtils.BUTTON_PRESSED, self.add_attachment)
		self.tab.set_focus_function(self.onFocus)

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True # Control variable for handling unauthorised/connection errors.
		try:
			num = getattr(self.session, "get_messages")(name=self.name, *self.args, **self.kwargs)
		except VkAPIMethodError as err:
			log.error(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, False) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		else:
			if num > 0:
				[self.insert(i, False) for i in self.session.db[self.name]["items"][:num]]
		return retrieved

	def add_attachment(self, *args, **kwargs):
		a = attach.attach(self.session)
		r = a.parse_attachments()
		if r != "":
			self.attachments_to_be_sent = r

	def send_chat_to_user(self, *args, **kwargs):
		text = self.tab.text.GetValue()
#		if text == "" and not hasattr(self, "attachments_to_be_sent"): return
		call_threaded(self._send_message, text=text)

	def _send_message(self, text):
#		try:
		if hasattr(self, "attachments_to_be_sent"):
			response = self.session.vk.client.messages.send(user_id=self.kwargs["user_id"], message=text, attachment=self.attachments_to_be_sent)
			print self.attachments_to_be_sent
		else:
			response = self.session.vk.client.messages.send(user_id=self.kwargs["user_id"], message=text)
#		except VkAPIMethodError as ex:
#			if ex.code == 9:
#				output.speak(_(u"You have been sending a message that is already sent. Try to update the buffer if you can't see the new message in the history."))
#		finally:
#			self.tab.text.SetValue("")

	def __init__(self, *args, **kwargs):
		super(chatBuffer, self).__init__(*args, **kwargs)
		self.reads = []

	def parse_attachments(self, post):
		attachments = []

		if post.has_key("attachments"):
			for i in post["attachments"]:
				# We don't need the photos_list attachment, so skip it.
				if i["type"] == "photos_list":
					continue
				attachments.append(add_attachment(i))
				self.attachments.append(i)
		self.tab.attachments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_attachment)
		self.tab.insert_attachments(attachments)

	def open_attachment(self, *args, **kwargs):
		index = self.tab.attachments.get_selected()
		attachment = self.attachments[index]
		if attachment["type"] == "audio":
			a = posts.audio(session=self.session, postObject=[attachment["audio"]])
			a.dialog.get_response()
			a.dialog.Destroy()
		if attachment["type"] == "link":
			output.speak(_(u"Opening URL..."), True)
			webbrowser.open_new_tab(attachment["link"]["url"])
		elif attachment["type"] == "doc":
			if attachment["doc"].has_key("preview") and attachment["doc"]["preview"].has_key("audio_msg"):
				link = attachment["doc"]["preview"]["audio_msg"]["link_mp3"]
				output.speak(_(u"Playing..."))
				player.player.play(url=dict(url=link), set_info=False)
			else:
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
		self.tab.list.list.SetItem(self.tab.list.get_selected(), 1, created_at)

	def open_timeline(self, *args, **kwargs):
		pass

	def get_menu(self, *args, **kwargs):
		m = menus.peopleMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.new_chat, menuitem=m.message)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_timeline, menuitem=m.timeline)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
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
			log.error(u"Error {0}: {1}".format(err.code, err.message))
			retrieved = err.code
			return retrieved
		num = self.session.get_page(name=self.name, show_nextpage=show_nextpage, endpoint="get", parent_endpoint="users", count=1000, user_ids=", ".join([str(i) for i in ids["items"]]), fields="uid, first_name, last_name, last_seen")
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		return retrieved
