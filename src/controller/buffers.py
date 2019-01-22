# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
from __future__ import unicode_literals
import time
import random
import logging
import webbrowser
import arrow
import wx
import presenters
import views
import interactors
import languageHandler
import widgetUtils
from presenters import player
import output
from . import selector
from pubsub import pub
from vk_api.exceptions import VkApiError
from vk_api import upload
from requests.exceptions import ReadTimeout, ConnectionError
from wxUI.tabs import home
from sessionmanager import session, renderers, utils
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus
from sessionmanager.renderers import add_attachment

log = logging.getLogger("controller.buffers")

class baseBuffer(object):
	""" a basic representation of a buffer. Other buffers should be derived from this class. This buffer represents the "news feed" """

	def get_post(self):
		""" Return the currently focused post."""
		# Handle case where there are no items in the buffer.
		if self.tab.list.get_count() == 0:
			wx.Bell()
			return None
		return self.session.db[self.name]["items"][self.tab.list.get_selected()]

	def __init__(self, parent=None, name="", session=None, composefunc=None, create_tab=True, *args, **kwargs):
		""" Constructor:
		@parent wx.Treebook: parent for the buffer panel,
		@name str: Name for saving this buffer's data in the local storage variable,
		@session sessionmanager.session.vkSession: Session for performing operations in the Vk API. This session should be logged in when this class is instanciated.
		@composefunc str: This function will be called for composing the result which will be put in the listCtrl. Composefunc should exist in the sessionmanager.renderers module.
		args and kwargs will be passed to get_items() without any filtering. Be careful there.
		"""
		super(baseBuffer, self).__init__()
		self.parent = parent
		self.args = args
		self.kwargs = kwargs
		self.session = session
		self.compose_function = composefunc
		self.name = name
		if create_tab:
			self.create_tab(self.parent)
		 #Update_function will be called every 3 minutes and it should be able to
		# Get all new items in the buffer and sort them properly in the CtrlList.
		# ToDo: Shall we allow dinamically set for update_function?
		self.update_function = "get_page"
		self.name = name
		# source_key and post_key will point to the keys for sender and posts in VK API objects.
		# They can be changed in the future for other item types in different buffers.
		self.user_key = "source_id"
		self.post_key = "post_id"
		# When set to False, update_function won't be executed here.
		self.can_get_items = True

	def create_tab(self, parent):
		""" Create the Wx panel."""
		self.tab = home.homeTab(parent)
		# Bind local events (they will respond to events happened in the buffer).
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def insert(self, item, reversed=False):
		""" Add a new item to the list. Uses renderers.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
		item_ = getattr(renderers, self.compose_function)(item, self.session)
		self.tab.list.insert_item(reversed, *item_)

	def get_items(self, show_nextpage=False):
		""" Retrieve items from the VK API. This function is called repeatedly by the main controller and users could call it implicitly as well with the update buffer option.
		@show_nextpage boolean: If it's true, it will try to load previous results.
		"""
		if self.can_get_items == False: return
		retrieved = True # Control variable for handling unauthorised/connection errors.
		try:
			num = getattr(self.session, "get_newsfeed")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		except VkApiError as err:
			log.error("Error {0}: {1}".format(err.code, err.error))
			retrieved = err.code
			return retrieved
		except ReadTimeout as ConnectionError:
			log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
			return False
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
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
		p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Write your post"), message="", text=""))
		if hasattr(p, "text") or hasattr(p, "privacy"):
			call_threaded(self.do_last, p=p)

	def do_last(self, p, parent_endpoint="wall", child_endpoint="post", *args, **kwargs):
		""" Second part of post function. Here everything is going to be sent to the API"""
		msg = p.text
		attachments = ""
		if hasattr(p, "attachments"):
			attachments = self.upload_attachments(p.attachments)
		urls = utils.find_urls_in_text(msg)
		if len(urls) != 0:
			if len(attachments) == 0: attachments = urls[0]
			else: attachments += urls[0]
			msg = msg.replace(urls[0], "")
		if msg != "":
			kwargs.update(message=msg)
		kwargs.update(privacy=p.privacy)
		if attachments != "":
			kwargs.update(attachments=attachments)
		# Determines the correct functions to call here.
		parent_endpoint = getattr(self.session.vk.client, parent_endpoint)
		endpoint = getattr(parent_endpoint, child_endpoint)
		post = endpoint(**kwargs)
		pub.sendMessage("posted", buffer=self.name)

	def upload_attachments(self, attachments):
		""" Upload attachments to VK before posting them.
		Returns attachments formatted as string, as required by VK API.
		Currently this function only supports photos and audios."""
		# To do: Check the caption and description fields for this kind of attachments.
		local_attachments = ""
		uploader = upload.VkUpload(self.session.vk.session_object)
		for i in attachments:
			if i["from"] == "online":
				local_attachments += "{0}{1}_{2},".format(i["type"], i["owner_id"], i["id"])
			elif i["from"] == "local" and i["type"] == "photo":
				photos = i["file"]
				description = i["description"]
				r = uploader.photo_wall(photos, caption=description)
				id = r[0]["id"]
				owner_id = r[0]["owner_id"]
				local_attachments += "photo{0}_{1},".format(owner_id, id)
			elif i["from"] == "local" and i["type"] == "audio":
				audio = i["file"]
				title = "untitled"
				artist = "unnamed"
				if "artist" in i:
					artist = i["artist"]
				if "title" in i:
					title = i["title"]
				r = uploader.audio(audio, title=title, artist=artist)
				id = r["id"]
				owner_id = r["owner_id"]
				local_attachments += "audio{0}_{1},".format(owner_id, id)
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
			self.tab.PopupMenu(menu, self.tab.list.list.GetPosition())

	def show_menu_by_key(self, ev):
		""" Show contextual menu when menu key is pressed"""
		if self.tab.list.get_count() == 0:
			return
		if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
			self.show_menu(widgetUtils.MENU, pos=self.tab.list.list.GetPosition())

	def get_menu(self):
		""" Returns contextual menu options. They will change according to the focused item"""
		p = self.get_post()
		if p == None:
			return
		# determine if the current user is able to delete the object.
		if "can_delete" in p:
			can_delete = True==p["can_delete"]
		else:
			can_delete = False
		m = menus.postMenu(can_delete=can_delete)
		if ("likes" in p) == False:
			m.like.Enable(False)
		elif p["likes"]["user_likes"] == 1:
			m.like.Enable(False)
			m.dislike.Enable(True)
		if ("comments" in p) == False:
			m.comment.Enable(False)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_like, menuitem=m.like)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_dislike, menuitem=m.dislike)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.do_comment, menuitem=m.comment)
		if hasattr(m, "view_profile"):
			widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
		if hasattr(m, "delete"):
			widgetUtils.connect_event(m, widgetUtils.MENU, self.delete, menuitem=m.delete)
		return m

	def do_like(self, *args, **kwargs):
		""" Set like in the currently focused post."""
		post = self.get_post()
		if post == None:
			return
		user = post[self.user_key]
		id = post[self.post_key]
		if "type" in post:
			type_ = post["type"]
		else:
			type_ = "post"
		l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 1
		# Translators: This will be used when user presses like.
		output.speak(_("You liked this"))

	def do_dislike(self, *args, **kwargs):
		""" Set dislike (undo like) in the currently focused post."""
		post = self.get_post()
		if post == None:
			return
		user = post[self.user_key]
		id = post[self.post_key]
		if "type" in post:
			type_ = post["type"]
		else:
			type_ = "post"
		l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
		self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 2
		# Translators: This will be user in 'dislike'
		output.speak(_("You don't like this"))

	def do_comment(self, *args, **kwargs):
		""" Make a comment into the currently focused post."""
		post = self.get_post()
		if post == None:
			return
		comment = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Add a comment"), message="", text="", mode="comment"))
		if hasattr(comment, "text") or hasattr(comment, "privacy"):
			msg = comment.text
			try:
				user = post[self.user_key]
				id = post[self.post_key]
				self.session.vk.client.wall.addComment(owner_id=user, post_id=id, text=msg)
				output.speak(_("You've posted a comment"))
			except Exception as msg:
				log.error(msg)

	def delete(self, *args, **kwargs):
		post = self.get_post()
		if ("type" in post and post["type"] == "post") or self.name != "newsfeed":
			question = commonMessages.remove_post()
			if question == widgetUtils.NO:
				return
			if "owner_id" in self.kwargs:
				result = self.session.vk.client.wall.delete(owner_id=self.kwargs["owner_id"], post_id=post[self.post_key])
			else:
				result = self.session.vk.client.wall.delete(post_id=post[self.post_key])
			pub.sendMessage("post_deleted", post_id=post[self.post_key])
			self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
			self.tab.list.remove_item(self.tab.list.get_selected())

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
		if post == None:
			return
		if "type" in post and post["type"] == "audio":
			pub.sendMessage("play-audio", audio_object=post["audio"]["items"][0])
			return True

	def open_person_profile(self, *args, **kwargs):
		""" Views someone's profile."""
		selected = self.get_post()
		if selected == None:
			return
		# Check all possible keys for an user object in VK API.
		keys = ["from_id", "source_id", "id"]
		for i in keys:
			if i in selected:
				pub.sendMessage("user-profile", person=selected[i])
				break

	def open_post(self, *args, **kwargs):
		""" Opens the currently focused post."""
		post = self.get_post()
		if post == None:
			return
		if "type" in post and post["type"] == "audio":
			a = presenters.displayAudioPresenter(session=self.session, postObject=post["audio"]["items"], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
		elif "type" in post and post["type"] == "friend":
			pub.sendMessage("open-post", post_object=post, controller_="displayFriendship")
		else:
			pub.sendMessage("open-post", post_object=post, controller_="displayPost")

	def pause_audio(self, *args, **kwargs):
		""" pauses audio playback."""
		player.player.pause()

	def remove_buffer(self, mandatory):
		""" Function for removing a buffer. Returns True if removal is successful, False otherwise"""
		return False

	def get_users(self):
		""" Returns source user in the post."""
		post = self.get_post()
		if post == None:
			return
		if ("type" in post) == False:
			return [post["from_id"]]
		else:
			return [post["source_id"]]

	def onFocus(self, *args,**kwargs):
		""" Function executed when the item in a list is selected.
		For this buffer it updates the date of posts in the list."""
		post = self.get_post()
		if post == None:
			return
		original_date = arrow.get(post["date"])
		created_at = original_date.humanize(locale=languageHandler.curLang[:2])
		self.tab.list.list.SetItem(self.tab.list.get_selected(), 2, created_at)

class feedBuffer(baseBuffer):
	""" This buffer represents an user's wall. It may be used either for the current user or someone else."""

	def get_items(self, show_nextpage=False):
		""" Update buffer with newest items or get older items in the buffer."""
		if self.can_get_items == False: return
		retrieved = True
		try:
			num = getattr(self.session, "get_page")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
		except VkApiError as err:
			log.error("Error {0}: {1}".format(err.code, err.error))
			retrieved = err.code
			return retrieved
		except ReadTimeout as ConnectionError:
			log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
			return False
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
			self.tab.name = self.name
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
			output.speak(_("This buffer can't be deleted"))
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
		self.can_post = True
		self.can_write_private_message = True
		# if this is an user timeline we must check permissions to hide buttons when needed.
		if "owner_id" in self.kwargs and self.kwargs["owner_id"] > 0:
			permissions = self.session.vk.client.users.get(user_ids=self.kwargs["owner_id"], fields="can_post, can_see_all_posts, can_write_private_message")
			self.can_post = permissions[0]["can_post"]
			self.can_see_all_posts = permissions[0]["can_see_all_posts"]
			self.can_write_private_message = permissions[0]["can_write_private_message"]

	def post(self, *args, **kwargs):
		""" Create a post in the wall for the specified user
		This process is handled in two parts. This is the first part, where the GUI is created and user can send the post.
		During the second part (threaded), the post will be sent to the API."""
		if "owner_id" not in self.kwargs:
			return super(feedBuffer, self).post()
		owner_id = self.kwargs["owner_id"]
		user = self.session.get_user(owner_id, key="user1")
		title = _("Post to {user1_nom]'s wall").format(**user)
		p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=title, message="", text=""))
		if hasattr(p, "text") or hasattr(p, "privacy"):
			call_threaded(self.do_last, p=p, owner_id=owner_id)

class communityBuffer(feedBuffer):

	def create_tab(self, parent):
		self.tab = home.communityTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		super(communityBuffer, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_community)

	def load_community(self, *args, **kwargs):
		output.speak(_("Loading community..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)

class audioBuffer(feedBuffer):
	""" this buffer was supposed to be used with audio elements
	but is deprecated as VK removed its audio support for third party apps."""

	def create_tab(self, parent):
		self.tab = home.audioTab(parent)
		self.tab.name = self.name
		self.connect_events()
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

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
		if selected < 0:
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
		if selected == -1:
			return
		audios = [self.session.db[self.name]["items"][selected]]
		a = presenters.displayAudioPresenter(session=self.session, postObject=audios, interactor=interactors.displayAudioInteractor(), view=views.displayAudio())

	def play_all(self, *args, **kwargs):
		selected = self.tab.list.get_selected()
		if selected == -1:
			selected = 0
		if self.name not in self.session.db:
			return
		audios = [i for i in self.session.db[self.name]["items"][selected:]]
		pub.sendMessage("play-audios", audios=audios)
		return True

	def remove_buffer(self, mandatory=False):
		if "me_audio" == self.name or "popular_audio" == self.name or "recommended_audio" == self.name:
			output.speak(_("This buffer can't be deleted"))
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
		output.speak(_("This buffer doesn't support getting more items."))

	def onFocus(self, *args, **kwargs):
		pass

	def add_to_library(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["audio_id"] = post["id"]
		if "album_id" in post:
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		audio = self.session.vk.client.audio.add(**args)
		if audio != None and int(audio) > 21:
			output.speak(_("Audio added to your library"))

	def remove_from_library(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["audio_id"] = post["id"]
		args["owner_id"] = self.session.user_id
		result = self.session.vk.client.audio.delete(**args)
		if int(result) == 1:
			output.speak(_("Removed audio from library"))
			self.tab.list.remove_item(self.tab.list.get_selected())

	def move_to_album(self, *args, **kwargs):
		if len(self.session.audio_albums) == 0:
			return commonMessages.no_audio_albums()
		post = self.get_post()
		if post == None:
			return
		album = selector.album(_("Select the album where you want to move this song"), self.session)
		if album.item == None: return
		id = post["id"]
		response = self.session.vk.client.audio.moveToAlbum(album_id=album.item, audio_ids=id)
		if response == 1:
		# Translators: Used when the user has moved an audio to an album.
			output.speak(_("Moved"))

	def get_menu(self):
		p = self.get_post()
		if p == None:
			return
		m = menus.audioMenu()
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.play_audio, menuitem=m.play)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_("&Remove from library"))
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
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		super(audioAlbum, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_album)

	def load_album(self, *args, **kwargs):
		output.speak(_("Loading album..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)
		self.tab.play.Enable(True)
		self.tab.play_all.Enable(True)

class videoBuffer(feedBuffer):
	""" This buffer represents video elements, and it can be used for showing videos for the logged user or someone else."""

	def create_tab(self, parent):
		self.tab = home.videoTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.play, widgetUtils.BUTTON_PRESSED, self.play_audio)
		super(videoBuffer, self).connect_events()

	def play_audio(self, *args, **kwargs):
		""" Due to inheritance this method should be called play_audio, but play the currently focused video.
		Opens a webbrowser pointing to the video's URL."""
		selected = self.tab.list.get_selected()
		if self.tab.list.get_count() == 0:
			return
		if selected == -1:
			selected = 0
		output.speak(_("Opening video in webbrowser..."))
		webbrowser.open_new_tab(self.session.db[self.name]["items"][selected]["player"])
#		print self.session.db[self.name]["items"][selected]
		return True

	def open_post(self, *args, **kwargs):
				pass

	def remove_buffer(self, mandatory=False):
		if "me_video" == self.name:
			output.speak(_("This buffer can't be deleted"))
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
		output.speak(_("This buffer doesn't support getting more items."))

	def onFocus(self, *args, **kwargs):
		pass

	def add_to_library(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["video_id"] = post["id"]
		if "album_id" in post:
			args["album_id"] = post["album_id"]
		args["owner_id"] = post["owner_id"]
		video = self.session.vk.client.video.add(**args)
		if video != None and int(video) > 21:
			output.speak(_("Video added to your library"))

	def remove_from_library(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		args = {}
		args["video_id"] = post["id"]
		args["owner_id"] = self.session.user_id
		result = self.session.vk.client.video.delete(**args)
		if int(result) == 1:
			output.speak(_("Removed video from library"))
			self.tab.list.remove_item(self.tab.list.get_selected())

	def move_to_album(self, *args, **kwargs):
		if len(self.session.video_albums) == 0:
			return commonMessages.no_video_albums()
		post= self.get_post()
		if post == None:
			return
		album = selector.album(_("Select the album where you want to move this video"), self.session, "video_albums")
		if album.item == None: return
		id = post["id"]
		response = self.session.vk.client.video.addToAlbum(album_ids=album.item, video_id=id, target_id=self.session.user_id, owner_id=self.get_post()["owner_id"])
		if response == 1:
		# Translators: Used when the user has moved an video  to an album.
			output.speak(_("Moved"))

	def get_menu(self):
		""" We'll use the same menu that is used for audio items, as the options are exactly the same"""
		p = self.get_post()
		if p == None:
			return
		m = menus.audioMenu()
#		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
#		widgetUtils.connect_event(m, widgetUtils.MENU, self.play_audio, menuitem=m.play)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.move_to_album, menuitem=m.move)
		# if owner_id is the current user, the audio is added to the user's audios.
		if p["owner_id"] == self.session.user_id:
			m.library.SetItemLabel(_("&Remove from library"))
			widgetUtils.connect_event(m, widgetUtils.MENU, self.remove_from_library, menuitem=m.library)
		else:
			widgetUtils.connect_event(m, widgetUtils.MENU, self.add_to_library, menuitem=m.library)
		return m

class videoAlbum(videoBuffer):

	def create_tab(self, parent):
		self.tab = home.videoAlbumTab(parent)
		self.tab.play.Enable(False)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		super(videoAlbum, self).connect_events()
		widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_album)

	def load_album(self, *args, **kwargs):
		output.speak(_("Loading album..."))
		self.can_get_items = True
		self.tab.load.Enable(False)
		wx.CallAfter(self.get_items)
		self.tab.play.Enable(True)

class empty(object):

	def __init__(self, name=None, parent=None, *args, **kwargs):
		self.tab = home.empty(parent=parent, name=name)
		self.name = name

	def get_items(self, *args, **kwargs):
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
			self.tab.name = self.name
		pass

	def get_more_items(self, *args, **kwargs):
		output.speak(_("This buffer doesn't support getting more items."))

	def remove_buffer(self, mandatory=False): return False

class chatBuffer(baseBuffer):

	def insert(self, item, reversed=False):
		""" Add a new item to the list. Uses session.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
		item_ = getattr(renderers, self.compose_function)(item, self.session)
		# the self.chat dictionary will have (first_line, last_line) as keys and message ID as a value for looking into it when needed.
		# Here we will get first and last line of a chat message appended to the history.
		values = self.tab.add_message(item_[0])
		self.chats[values] = item["id"]

	def get_focused_post(self):
		""" Gets chat message currently in focus"""
		# this function replaces self.get_post for normal buffers, as we rely in a TextCtrl control for getting chats.
		# Instead of the traditional method to do the trick.
		# Get text position here.
		position = self.tab.history.PositionToXY(self.tab.history.GetInsertionPoint())
		id_ = None
		for i in list(self.chats.keys()):
			# Check if position[2] (line position) matches with something in self.chats
			# (All messages, except the last one, should be able to be matched here).
			# position[2]+1 is added because line may start with 0, while in wx.TextCtrl.GetNumberLines() that is not possible.
			if position[2]+1 >= i[0] and position[2]+1 < i[1]:
				id_ = self.chats[i]
#				print i
				break
		# Retrieve here the object based in id_
		if id_ != None:
			for i in self.session.db[self.name]["items"]:
				if i["id"] == id_:
					return i
		return False

	get_post = get_focused_post

	def onFocus(self, event, *args, **kwargs):
		if event.GetKeyCode() == wx.WXK_UP or event.GetKeyCode() == wx.WXK_DOWN or event.GetKeyCode() == wx.WXK_START or event.GetKeyCode() == wx.WXK_PAGEUP or event.GetKeyCode() == wx.WXK_PAGEDOWN or event.GetKeyCode() == wx.WXK_END:
			msg = self.get_focused_post()
			if msg == False: # Handle the case where the last line of the control cannot be matched to anything.
				return
			if "read_state" in msg and msg["read_state"] == 0 and msg["id"] not in self.reads and "out" in msg and msg["out"] == 0:
				self.session.soundplayer.play("message_unread.ogg")
				self.reads.append(msg["id"])
				self.session.db[self.name]["items"][-1]["read_state"] = 1
			if "attachments" in msg and len(msg["attachments"]) > 0:
				self.tab.attachments.list.Enable(True)
				self.attachments = list()
				self.tab.attachments.clear()
				self.parse_attachments(msg)
			else:
				self.tab.attachments.list.Enable(False)
				self.tab.attachments.clear()
		event.Skip()

	def create_tab(self, parent):
		self.tab = home.chatTab(parent)
		self.attachments = list()
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		widgetUtils.connect_event(self.tab.send, widgetUtils.BUTTON_PRESSED, self.send_chat_to_user)
		widgetUtils.connect_event(self.tab.attachment, widgetUtils.BUTTON_PRESSED, self.add_attachment)
		widgetUtils.connect_event(self.tab.text, widgetUtils.KEYPRESS, self.catch_enter)
		self.tab.set_focus_function(self.onFocus)

	def catch_enter(self, event, *args, **kwargs):
		shift=event.ShiftDown()
		if event.GetKeyCode() == wx.WXK_RETURN and shift == False:
			return self.send_chat_to_user()
		t = time.time()
		if event.GetUnicodeKey() != wx.WXK_NONE and t-self.last_keypress > 5:
			self.last_keypress = t
			call_threaded(self.session.vk.client.messages.setActivity, peer_id=self.kwargs["peer_id"], type="typing")
		event.Skip()

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True # Control variable for handling unauthorised/connection errors.
		try:
			num = getattr(self.session, "get_messages")(name=self.name, *self.args, **self.kwargs)
		except VkApiError as err:
			log.error("Error {0}: {1}".format(err.code, err.error))
			retrieved = err.code
			return retrieved
		except ReadTimeout as ConnectionError:
			log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
			return False
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
			self.tab.name = self.name
		if show_nextpage  == False:
			if self.tab.history.GetValue() != "" and num > 0:
				v = [i for i in self.session.db[self.name]["items"][:num]]
#				v.reverse()
				[self.insert(i, False) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		else:
			if num > 0:
				[self.insert(i, False) for i in self.session.db[self.name]["items"][:num]]
		if self.unread == True and num > 0:
			self.session.db[self.name]["items"][-1].update(read_state=0)
		return retrieved

	def add_attachment(self, *args, **kwargs):
		a = presenters.attachPresenter(session=self.session, view=views.attachDialog(voice_messages=True), interactor=interactors.attachInteractor())
		if len(a.attachments) != 0:
			self.attachments_to_be_sent = a.attachments

	def send_chat_to_user(self, *args, **kwargs):
		text = self.tab.text.GetValue()
		if text == "" and not hasattr(self, "attachments_to_be_sent"):
			wx.Bell()
			return
		self.tab.text.SetValue("")
		call_threaded(self._send_message, text=text)

	def upload_attachments(self, attachments):
		""" Upload attachments to VK before posting them.
		Returns attachments formatted as string, as required by VK API.
		"""
		local_attachments = ""
		uploader = upload.VkUpload(self.session.vk.session_object)
		for i in attachments:
			if i["from"] == "online":
				local_attachments += "{0}{1}_{2},".format(i["type"], i["owner_id"], i["id"])
			elif i["from"] == "local" and i["type"] == "photo":
				photos = i["file"]
				description = i["description"]
				r = uploader.photo_messages(photos)
				id = r[0]["id"]
				owner_id = r[0]["owner_id"]
				local_attachments += "photo{0}_{1},".format(owner_id, id)
			elif i["from"] == "local" and i["type"] == "audio":
				audio = i["file"]
				title = "untitled"
				artist = "unnamed"
				if "artist" in i:
					artist = i["artist"]
				if "title" in i:
					title = i["title"]
				r = uploader.audio(audio, title=title, artist=artist)
				id = r["id"]
				owner_id = r["owner_id"]
				local_attachments += "audio{0}_{1},".format(owner_id, id)
			elif i["from"] == "local" and i["type"] == "voice_message":
				r = uploader.audio_message(i["file"], peer_id=self.kwargs["peer_id"])
				id = r["audio_message"]["id"]
				owner_id = r["audio_message"]["owner_id"]
				local_attachments += "audio_message{0}_{1},".format(owner_id, id)
		return local_attachments

	def _send_message(self, text, attachments=[]):
		if hasattr(self, "attachments_to_be_sent"):
			self.attachments_to_be_sent = self.upload_attachments(self.attachments_to_be_sent)
		try:
		# Let's take care about the random_id attribute.
		# This should be unique per message and should be changed right after the message has been sent.
		# If the message is tried to be sent twice this random_id should be the same for both copies.
		# At the moment we just calculate len(text)_user_id, hope that will work.
			random_id = random.randint(0, 100000)
			if hasattr(self, "attachments_to_be_sent"):
				response = self.session.vk.client.messages.send(peer_id=self.kwargs["peer_id"], message=text, attachment=self.attachments_to_be_sent, random_id=random_id)
			else:
				response = self.session.vk.client.messages.send(peer_id=self.kwargs["peer_id"], message=text, random_id=random_id)
		except ValueError as ex:
			if ex.code == 9:
				output.speak(_("You have been sending a message that is already sent. Try to update the buffer if you can't see the new message in the history."))

	def __init__(self, unread=False, *args, **kwargs):
		super(chatBuffer, self).__init__(*args, **kwargs)
		self.unread = unread
		self.reads = []
		self.chats = dict()
		self.peer_typing = 0
		self.last_keypress = time.time()

	def parse_attachments(self, post):
		attachments = []

		if "attachments" in post:
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
			a = presenters.displayAudioPresenter(session=self.session, postObject=[attachment["audio"]], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
		elif attachment["type"] == "audio_message":
			link = attachment["audio_message"]["link_mp3"]
			output.speak(_("Playing..."))
			player.player.play(url=dict(url=link), set_info=False)
		elif attachment["type"] == "link":
			output.speak(_("Opening URL..."), True)
			webbrowser.open_new_tab(attachment["link"]["url"])
		elif attachment["type"] == "doc":
			output.speak(_("Opening document in web browser..."))
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
			output.speak(_("Opening video in web browser..."), True)
			webbrowser.open_new_tab(video_object["player"])
		elif attachment["type"] == "photo":
			output.speak(_("Opening photo in web browser..."), True)
			# Possible photo sizes for looking in the attachment information. Try to use the biggest photo available.
			possible_sizes = [1280, 604, 130, 75]
			url = ""
			for i in possible_sizes:
				if "photo_{0}".format(i,) in attachment["photo"]:
					url = attachment["photo"]["photo_{0}".format(i,)]
					break
			if url != "":
				webbrowser.open_new_tab(url)
		else:
			log.debug("Unhandled attachment: %r" % (attachment,))

	def clear_reads(self):
		for i in self.session.db[self.name]["items"]:
			if "read_state" in i and i["read_state"] == 0:
				i["read_state"] = 1

	def remove_buffer(self, mandatory=False):
		""" Remove buffer if the current buffer is not the logged user's wall."""
		if mandatory == False:
			dlg = commonMessages.remove_buffer()
		else:
			dlg = widgetUtils.YES
		if dlg == widgetUtils.YES:
			self.session.db.pop(self.name)
			return True
		else:
			return False

class peopleBuffer(feedBuffer):

	def create_tab(self, parent):
		self.tab = home.peopleTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)

	def connect_events(self):
		super(peopleBuffer, self).connect_events()
		widgetUtils.connect_event(self.tab.new_chat, widgetUtils.BUTTON_PRESSED, self.new_chat)

	def new_chat(self, *args, **kwargs):
		user = self.get_post()
		if user == None:
			return
		user_id = user["id"]
		pub.sendMessage("new-chat", user_id=user_id)

	def onFocus(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		if ("last_seen" in post) == False: return
		original_date = arrow.get(post["last_seen"]["time"])
		created_at = original_date.humanize(locale=languageHandler.curLang[:2])
		self.tab.list.list.SetItem(self.tab.list.get_selected(), 1, created_at)

	def open_timeline(self, *args, **kwargs):
		pass

	def get_menu(self, *args, **kwargs):
		""" display menu for people buffers (friends and requests)"""
		# If this is an incoming requests buffer, there is a flag in the peopleMenu that shows a few new options.
		# So let's make sure we call it accordingly.
		if self.name == "friend_requests":
			m = menus.peopleMenu(is_request=True)
			# Connect the accept and decline methods from here.
			widgetUtils.connect_event(m, widgetUtils.MENU, self.accept_friendship, menuitem=m.accept)
			widgetUtils.connect_event(m, widgetUtils.MENU, self.decline_friendship, menuitem=m.decline)
			widgetUtils.connect_event(m, widgetUtils.MENU, self.keep_as_follower, menuitem=m.keep_as_follower)
		elif self.name == "subscribers":
			m = menus.peopleMenu(is_subscriber=True)
			widgetUtils.connect_event(m, widgetUtils.MENU, self.accept_friendship, menuitem=m.add)
		else:
			m = menus.peopleMenu(is_request=False)
		# It is not allowed to send messages to people who is not your friends, so let's disable it if we're in a pending or outgoing requests folder.
		if "friend_requests" in self.name:
			m.message.Enable(False)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.new_chat, menuitem=m.message)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_timeline, menuitem=m.timeline)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
		return m

	def open_post(self, *args, **kwargs): pass

	def play_audio(self, *args, **kwargs): return False

	def pause_audio(self, *args, **kwargs): pass

	def accept_friendship(self, *args, **kwargs):
		pass

	def decline_friendship(self, *args, **kwargs):
		person = self.get_post()
		if person == None:
			return
		user = self.session.get_user(person["id"])
		question = commonMessages.remove_friend(user)
		if question == widgetUtils.NO:
			return
		result = self.session.vk.client.friends.delete(user_id=person["id"])
		if "friend_deleted" in result:
			msg = _("You've deleted {user1_nom} from your friends.").format(**user,)
		print(msg)
		pub.sendMessage("notify", message=msg)
		self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
		self.tab.list.remove_item(self.tab.list.get_selected())

	def keep_as_follower(self, *args, **kwargs):
		pass

class requestsBuffer(peopleBuffer):

	def get_items(self, show_nextpage=False):
		if self.can_get_items == False: return
		retrieved = True
		try:
			ids = self.session.vk.client.friends.getRequests(*self.args, **self.kwargs)
		except VkApiError as err:
			log.error("Error {0}: {1}".format(err.code, err.error))
			retrieved = err.code
			return retrieved
		except ReadTimeout as ConnectionError:
			log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
			return False
		num = self.session.get_page(name=self.name, show_nextpage=show_nextpage, endpoint="get", parent_endpoint="users", count=1000, user_ids=", ".join([str(i) for i in ids["items"]]), fields="uid, first_name, last_name, last_seen")
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
			self.tab.name = self.name
		if show_nextpage  == False:
			if self.tab.list.get_count() > 0 and num > 0:
				v = [i for i in self.session.db[self.name]["items"][:num]]
				v.reverse()
				[self.insert(i, True) for i in v]
			else:
				[self.insert(i) for i in self.session.db[self.name]["items"][:num]]
		return retrieved

	def accept_friendship(self, *args, **kwargs):
		""" Adds a person to a list of friends. This method is done for accepting someone else's friend request.
		https://vk.com/dev/friends.add
		"""
		person = self.get_post()
		if person == None:
			return
		result = self.session.vk.client.friends.add(user_id=person["id"])
		if result == 2:
			msg = _("{0} {1} now is your friend.").format(person["first_name"], person["last_name"])
			pub.sendMessage("notify", message=msg)
			self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
			self.tab.list.remove_item(self.tab.list.get_selected())

	def decline_friendship(self, *args, **kwargs):
		""" Declines a freind request.
		https://vk.com/dev/friends.delete
		"""
		person = self.get_post()
		if person == None:
			return
		result = self.session.vk.client.friends.delete(user_id=person["id"])
		if "out_request_deleted" in result:
			msg = _("You've deleted the friends request to {0} {1}.").format(person["first_name"], person["last_name"])
		elif "in_request_deleted" in result:
			msg = _("You've declined the friend request of {0} {1}.").format(person["first_name"], person["last_name"])
		pub.sendMessage("notify", message=msg)
		self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
		self.tab.list.remove_item(self.tab.list.get_selected())

	def keep_as_follower(self, *args, **kwargs):
		""" Adds a person to The followers list of the current user.
		https://vk.com/dev/friends.add
		"""
		person = self.get_post()
		if person == None:
			return
		result = self.session.vk.client.friends.add(user_id=person["id"], follow=1)
		if result == 2:
			msg = _("{0} {1} is following you.").format(person["first_name"], person["last_name"])
			pub.sendMessage("notify", message=msg)
			self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
			self.tab.list.remove_item(self.tab.list.get_selected())