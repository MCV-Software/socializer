# -*- coding: utf-8 -*-
""" Session object for Socializer. A session is the only object to call VK API methods, save settings and access to the cache database and sound playback mechanisms. """
from __future__ import unicode_literals
import os
import logging
import warnings
import wx
import languageHandler
import paths
import config
import sound
from requests.exceptions import ProxyError, ConnectionError
from pubsub import pub
from vk_api.exceptions import LoginRequired, VkApiError
from vk_api import upload
from .config_utils import Configuration, ConfigurationResetException
from . import vkSessionHandler
from . import utils

log = logging.getLogger("session")

sessions = {}

# Save possible set of identifier keys for VK'S data types
# see https://vk.com/dev/datatypes for more information.
# I've added the Date identifier (this is a field in unix time format), for special objects (like friendship indicators) because these objects don't have an own identifier.
identifiers = ["aid", "gid", "uid", "pid", "id", "post_id", "nid", "date"]

# Different VK post types, present in the newsfeed buffer. This is useful for filtering by post and remove deleted posts.
post_types = dict(audio="audio", friend="friends", video="files", post="post_type", audio_playlist="audio_playlist")

def find_item(list, item):
	""" Find an item in a list  by taking an identifier.
	@list list: A list of dict objects.
	@ item dict: A dictionary containing at least an identifier.
	"""
	# determine the kind of identifier that we are using
	global identifiers
	identifier = None
	for i in identifiers:
		if i in item:
			identifier =   i
			break
	if identifier == None:
		# if there are objects that can't be processed by lack of identifier, let's print  keys for finding one.
		log.exception("Can't find an identifier for the following object: %r" % (item,))
		return False
	for i in list:
		if identifier in i and i[identifier] == item[identifier]:
			return True
	return False

class vkSession(object):
	""" The only session available in socializer. Manages everything related to a model in an MVC app: calls to VK, sound handling, settings and a cache database."""

	def order_buffer(self, name, data, show_nextpage):
		""" Put new items on the local cache database.
		@name str: The name for the buffer stored in the dictionary.
		@data list: A list with items and some information about cursors.
		returns the number of items that have been added in this execution"""
		global post_types
		# When this method is called by friends.getOnlyne, it gives only friend IDS so we need to retrieve full objects from VK.
		# ToDo: It would be nice to investigate whether reusing some existing objects would be a good idea, whenever possible.
		if name == "online_friends":
			newdata = self.vk.client.users.get(user_ids=",".join([str(z) for z in data]), fields="last_seen")
			data = newdata
		first_addition = False
		num = 0
		if (name in self.db) == False:
			self.db[name] = {}
			self.db[name]["items"] = []
			first_addition = True
		# Handles chat messages case, as the buffer is inverted
		if name.endswith("_messages") and show_nextpage == True:
			show_nextpage = False
		for i in data:
			if "type" in i and (i["type"] == "wall_photo" or i["type"] == "photo_tag" or i["type"] == "photo" or i["type"] == False or i["type"] == True):
				log.debug("Skipping unsupported item... %r" % (i,))
				continue
			# for some reason, VK sends post data if the post has been deleted already.
			# Example of this behaviour is when you upload an audio and inmediately delete the audio, VK still sends the post stating that you uploaded an audio file,
			# But without the audio data, making socializer to render an empty post.
			# Here we check if the post contains data of the type it advertises.
			if i.get("type") != None and isinstance(i["type"], str) and post_types.get(i["type"]) not in i:
				log.error("Detected invalid or unsupported post. Skipping...")
				log.error(i)
				continue
			if find_item(self.db[name]["items"], i) == False:
#			if i not in self.db[name]["items"]:
				if first_addition == True or show_nextpage == True:
					if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].append(i)
					else: self.db[name]["items"].insert(0, i)
				else:
					if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].insert(0, i)
					else: self.db[name]["items"].append(i)
				num = num+1
		log.debug("There are %d items in the %s buffer" % (len(self.db[name]["items"]), name))
		return num

	def __init__(self, session_id):
		self.session_id = session_id
		self.logged = False
		self.settings = None
		self.vk = vkSessionHandler.vkObject()
		self.db = {}
		self.db["users"] = {}
		self.db["groups"] = {}
		self.db["group_info"] = {}

	@property
	def is_logged(self):
		return self.logged

	def get_configuration(self, nosound=False):

		""" Gets settings for a session."""
 
		file_ = "%s/session.conf" % (self.session_id,)
#  try:
		log.debug("Creating config file %s" % (file_,))
		self.settings = Configuration(os.path.join(paths.config_path(), file_), os.path.join(paths.app_path(), "session.defaults"))
		if nosound == False:
			self.soundplayer = sound.soundSystem(config.app["sound"])
			pub.subscribe(self.play_sound, "play-sound")
			pub.subscribe(self.post, "post")
#  except:
#   log.exception("The session configuration has failed.")

	def play_sound(self, sound):
		self.soundplayer.play(sound)

	def login(self):
		""" Logging in VK.com. This is basically the first method interacting with VK. """
		# If user is already logged in, we should skip this method.
		if self.logged == True:
			return
		try:
			config_filename = os.path.join(paths.config_path(), self.session_id, "vkconfig.json")
			self.vk.login(self.settings["vk"]["user"], self.settings["vk"]["password"], token=self.settings["vk"]["token"], secret=self.settings["vk"]["secret"], device_id=self.settings["vk"]["device_id"], alt_token=self.settings["vk"]["use_alternative_tokens"], filename=config_filename)
			self.settings["vk"]["token"] = self.vk.session_object.token["access_token"]
			try:
				self.settings["vk"]["secret"] = self.vk.session_object.secret
				self.settings["vk"]["device_id"] = self.vk.session_object.device_id
			except AttributeError:
				pass
			self.settings.write()
			self.logged = True
			self.get_my_data()
		except VkApiError as error:
			if error.code == 5: # this means invalid access token.
				self.settings["vk"]["user"] = ""
				self.settings["vk"]["password"] = ""
				self.settings["vk"]["token"] = ""
				self.settings["vk"]["secret"] = ""
				self.settings["vk"]["device_id"] = ""
				self.settings.write()
				pub.sendMessage("authorisation-failed")
			else: # print out error so we we will handle it in future versions.
				log.exception("Fatal error when authenticating the application.")
				log.exception(error.code)
				log.exception(error.message)
		except (ProxyError, ConnectionError):
			pub.sendMessage("connection_error")

	def post_wall_status(self, message, *args, **kwargs):
		""" Sends a post to an user, group or community wall."""
		log.debug("Making a post to the user's wall with the following params: %r" % (kwargs,))
		response = self.vk.client.wall.post(message=message, *args, **kwargs)

	def get_newsfeed(self, name="newsfeed", show_nextpage=False, endpoint="", *args, **kwargs):
		log.debug("Updating news feed...")
		if show_nextpage == True and "cursor" in self.db[name]:
			log.debug("user has requested previous items")
			kwargs["start_from"] = self.db[name]["cursor"]
			log.debug("Params for sending to vk: %r" % (kwargs,))
		data = getattr(self.vk.client.newsfeed, "get")(*args, **kwargs)
		if data != None:
			self.process_usernames(data)
			num = self.order_buffer(name, data["items"], show_nextpage)
			log.debug("Keys of the returned data for debug purposes: %r" % (list(data.keys()),))
			if "next_from" in data:
				self.db[name]["cursor"] = data["next_from"]
				log.debug("Next cursor saved for data: {cursor}".format(cursor=data["next_from"]))
			return num

	def get_page(self, name="", show_nextpage=False, endpoint="", *args, **kwargs):
		data = None
		if "audio" in endpoint and self.settings["vk"]["use_alternative_tokens"]:
			log.info("Using alternative audio methods.")
			c = self.vk.client_audio
		else:
			c = self.vk.client
		formatted_endpoint = ""
		if "parent_endpoint" in kwargs:
			p = kwargs["parent_endpoint"]
			formatted_endpoint = kwargs["parent_endpoint"]
			if "audio" in p and self.settings["vk"]["use_alternative_tokens"]:
				log.info("Using alternative audio methods.")
				c = self.vk.client_audio
			kwargs.pop("parent_endpoint")
		try:
			p = getattr(c, p)
		except AttributeError:
			p = c
		if name in self.db and "offset" in self.db[name] and show_nextpage == True:
			kwargs.update(offset=self.db[name]["offset"])
		else:
			kwargs.update(offset=0)
		formatted_endpoint = "{formatted_endpoint}.{new_path}".format(formatted_endpoint=formatted_endpoint, new_path=endpoint)
		offset_deprecated = ["notifications.get"]
		if formatted_endpoint in offset_deprecated:
			kwargs.update(offset=None)
		log.debug("Calling endpoint %s with params %r" % (formatted_endpoint, kwargs,))
		data = getattr(p, endpoint)(*args, **kwargs)
		if data != None:
			if "count" not in kwargs:
				kwargs["count"] = 100
			# Let's handle a little exception when dealing with conversation buffers.
			# the first results of the query should be reversed before being sent to order_buffer.
			if type(data) == dict and "items" in data and endpoint == "getHistory" and kwargs["offset"] == 0:
				data["items"].reverse()
			if type(data) == dict:
				num = self.order_buffer(name, data["items"], show_nextpage)
				if formatted_endpoint not in offset_deprecated:
					self.db[name]["offset"] = kwargs["offset"]+kwargs["count"]
				if len(data["items"]) > 0 and "first_name" in data["items"][0]:
					data2 = {"profiles": [], "groups": []}
					for i in data["items"]:
						data2["profiles"].append(i)
					self.process_usernames(data2)
				if "profiles" in data and "groups" in data:
					self.process_usernames(data)
			else:
				num = self.order_buffer(name, data, show_nextpage)
				self.db[name]["offset"] = kwargs["offset"]+kwargs["count"]
			return num

	def get_messages(self, name="", *args, **kwargs):
		data = self.vk.client.messages.getHistory(*args, **kwargs)
		data["items"].reverse()
		if data != None:
			num = self.order_buffer(name, data["items"], False)
			return num

	def get_users(self, user_ids=None, group_ids=None):
		log.debug("Getting user information from the VK servers")
		if user_ids != None:
			u = self.vk.client.users.get(user_ids=user_ids, fields="uid, first_name, last_name")
			for i in u:
				self.db["users"][i["id"]] = dict(nom="{0} {1}".format(i["first_name"], i["last_name"]))
		if group_ids != None:
			g = self.vk.client.groups.getById(group_ids=group_ids, fields="name")
			for i in g:
				self.db["groups"][i["id"]] = dict(nom=i["name"], gen=i["name"], dat=i["name"], acc=i["name"], ins=i["name"], abl=i["name"])

	def get_user(self, user_id, key="user1"):
		if user_id > 0:
			if user_id in self.db["users"]:
				user_data = {}
				user_fields = "nom, gen, ins, dat, abl, acc".split(", ")
				for i in user_fields:
					k = "{key}_{case}".format(key=key, case=i)
					v = "{first_name} {last_name}".format(first_name=self.db["users"][user_id]["first_name_"+i], last_name=self.db["users"][user_id]["last_name_"+i])
					user_data[k] = v
				return user_data
			# if User_id is not present in db.
			else:
				user = dict(id=user_id)
				self.process_usernames(data=dict(profiles=[user], groups=[]))
				return self.get_user(user_id)
		else:
			if abs(user_id) in self.db["groups"]:
				user_data = {}
				user_fields = "nom, gen, ins, dat, abl, acc".split(", ")
				for i in user_fields:
					k = "{key}_{case}".format(key=key, case=i)
					v = self.db["groups"][abs(user_id)][i]
					user_data[k] = v
			else:
				group = self.vk.client.groups.getById(group_ids=-1*user_id)[0]
				self.process_usernames(data=dict(profiles=[], groups=[group]))
				return self.get_user(user_id=user_id, key=key)
			return user_data

	def process_usernames(self, data):
		""" processes user IDS and saves them in a local storage system.
		Every function wich needs to convert from an ID to user or community name will have to call the get_user_name function in this session object.
		Every function that needs to save a set ot user ids for a future use needs to pass a data dictionary with a profiles key being a list of user objects.
		It gets first and last name for people in the 6 russian cases and saves them for future reference."""
		log.debug("Adding usernames to the local database...")
		ids = ""
		for i in data["profiles"]:
			if (i["id"] in self.db["users"]) == False:
				ids = ids + "{0},".format(i["id"],)
		gids = ""
		for i in data["groups"]:
			if i["id"] not in self.db["groups"]:
				self.db["groups"][i["id"]] = dict(nom=i["name"], gen=i["name"], dat=i["name"], acc=i["name"], ins=i["name"], abl=i["name"])
				gids = "{0},".format(i["id"],)
		user_fields = "first_name_nom, last_name_nom, first_name_gen, last_name_gen, first_name_ins, last_name_ins, first_name_dat, last_name_dat, first_name_abl, last_name_abl, first_name_acc, last_name_acc, sex"
		user_fields_list = user_fields.split(", ")
		if ids != "":
			users = self.vk.client.users.get(user_ids=ids, fields=user_fields)
			for i in users:
				if i["id"] not in self.db["users"]:
					userdata = {}
					for field in user_fields_list:
						if field in i:
							userdata[field] = i[field]
					self.db["users"][i["id"]] = userdata

	def get_my_data(self):
		log.debug("Getting user identifier...")
		user = self.vk.client.users.get(fields="uid, first_name, last_name")
		self.user_id = user[0]["id"]

	def post(self, parent_endpoint, child_endpoint, from_buffer=None, attachments_list=[], post_arguments={}):
		""" Generic function to be called whenever user wants to post something to VK.
		This function should be capable of uploading all attachments before posting, and send a special event in case the post has failed,
		So the program can recreate the post and show it back to the user."""
		# ToDo: this function will occasionally be called with attachments already set to post_arguments, example if the user could upload the files but was unable to send the post due to a connection problem.
		# We should see what can be done (reuploading everything vs using the already added attachments).
		attachments = ""
		# Firstly, let's try to upload the attachments here. If peer_id exists in post_arguments,
		# It means we are talking about private messages, whose attachment procedures have their own methods.
		if len(attachments_list) > 0:
			try:
				attachments = self.upload_attachments(attachments_list, post_arguments.get("peer_id"))
			except Exception as error:
				log.error("Error calling method %s.%s with arguments: %r. Failed during loading attachments. Error: %s" % (parent_endpoint, child_endpoint, post_arguments, str(error)))
				# Report a failed function here too with same arguments so the client should be able to recreate it again.
				wx.CallAfter(pub.sendMessage, "postFailed", parent_endpoint=parent_endpoint, child_endpoint=child_endpoint, from_buffer=from_buffer, attachments_list=attachments_list, post_arguments=post_arguments)
		# VK generally defines all kind of messages under "text", "message" or "body" so let's try with all of those
		possible_message_keys = ["text", "message", "body"]
		for i in possible_message_keys:
			if post_arguments.get(i):
				urls = utils.find_urls_in_text(post_arguments[i])
				if len(urls) != 0:
					if len(attachments) == 0:
						attachments = urls[0]
					else:
						attachments += urls[0]
					post_arguments[i] = post_arguments[i].replace(urls[0], "")
		# After modifying everything, let's update the post arguments if needed.
		if len(attachments) > 0:
			if parent_endpoint == "messages":
				post_arguments.update(attachment=attachments)
			else:
				post_arguments.update(attachments=attachments)
		# Determines the correct functions to call here.
		endpoint = getattr(self.vk.client, parent_endpoint)
		endpoint = getattr(endpoint, child_endpoint)
		try:
			post = endpoint(**post_arguments)
			# Once the post has been send, let's report it to the interested objects.
			pub.sendMessage("posted", from_buffer=from_buffer)
		except Exception as error:
			log.exception("Error calling method %s.%s with arguments: %r. Error: %s" % (parent_endpoint, child_endpoint, post_arguments, str(error)))
			# Report a failed function here too with same arguments so the client should be able to recreate it again.
			wx.CallAfter(pub.sendMessage, "postFailed", parent_endpoint=parent_endpoint, child_endpoint=child_endpoint, from_buffer=from_buffer, attachments_list=attachments_list, post_arguments=post_arguments)

	def upload_attachments(self, attachments, peer_id=None):
		""" Upload attachments to VK before posting them.
		Returns attachments formatted as string, as required by VK API.
		@ peer_id int: if this value is passed, let's assume attachments will be send in private messages.
		"""
		# To do: Check the caption and description fields for this kind of attachments.
		local_attachments = ""
		uploader = upload.VkUpload(self.vk.session_object)
		for i in attachments:
			if i["from"] == "online":
				local_attachments += "{0}{1}_{2},".format(i["type"], i["owner_id"], i["id"])
			elif i["from"] == "local" and i["type"] == "photo":
				photos = i["file"]
				description = i["description"]
				if peer_id == None:
					r = uploader.photo_wall(photos, caption=description)
				else:
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
				r = uploader.audio_message(i["file"], peer_id=peer_id)
				id = r["audio_message"]["id"]
				owner_id = r["audio_message"]["owner_id"]
				local_attachments += "audio_message{0}_{1},".format(owner_id, id)
			elif i["from"] == "local" and i["type"] == "document":
				document = i["file"]
				title = i["title"]
				if peer_id == None:
					r = uploader.document(document, title=title, to_wall=True)
				else:
					r = uploader.document(document, title=title, message_peer_id=peer_id)
				id = r["doc"]["id"]
				owner_id = r["doc"]["owner_id"]
				local_attachments += "doc{0}_{1},".format(owner_id, id)
		return local_attachments