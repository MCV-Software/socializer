# -*- coding: utf-8 -*-
""" Session object for Socializer. A session is the only object to call VK API methods, save settings and access to the cache database and sound playback mechanisms. """
from __future__ import unicode_literals
import os
import logging
import warnings
import languageHandler
import paths
from . import vkSessionHandler
import sound
from .config_utils import Configuration, ConfigurationResetException
from pubsub import pub
from vk_api.exceptions import LoginRequired, VkApiError

log = logging.getLogger("session")

sessions = {}

# Save possible set of identifier keys for VK'S data types
# see https://vk.com/dev/datatypes for more information.
# I've added the Date identifier (this is a field in unix time format), for special objects (like friendship indicators) because these objects don't have an own identifier.
identifiers = ["aid", "gid", "uid", "pid", "id", "post_id", "nid", "date"]

# Different VK post types, present in the newsfeed buffer. This is useful for filtering by post and remove deleted posts.
post_types = dict(audio="audio", friend="friends", video="video", post="post_type", audio_playlist="audio_playlist")

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
		log.exception("Can't find an identifier for the following object: %r" % (list(item.keys()),))
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
		returns the number of items that has been added in this execution"""
		global post_types
		first_addition = False
		num = 0
		if (name in self.db) == False:
			self.db[name] = {}
			self.db[name]["items"] = []
			first_addition = True
		for i in data:
			if "type" in i and (i["type"] == "wall_photo" or i["type"] == "photo_tag" or i["type"] == "photo"):
				log.debug("Skipping unsupported item... %r" % (i,))
				continue
			# for some reason, VK sends post data if the post has been deleted already.
			# Example of this behaviour is when you upload an audio and inmediately delete the audio, VK still sends the post stating that you uploaded an audio file,
			# But without the audio data, making socializer to render an empty post.
			# Here we check if the post contains data of the type it advertises.
			if i.get("type") != None and post_types.get(i["type"]) not in i:
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

	@property
	def is_logged(self):
		return self.logged

	def get_configuration(self):

		""" Gets settings for a session."""
 
		file_ = "%s/session.conf" % (self.session_id,)
#  try:
		log.debug("Creating config file %s" % (file_,))
		self.settings = Configuration(os.path.join(paths.config_path(), file_), os.path.join(paths.app_path(), "session.defaults"))
		self.soundplayer = sound.soundSystem(self.settings["sound"])
#  except:
#   log.exception("The session configuration has failed.")

	def login(self):
		try:
			config_filename = os.path.join(paths.config_path(), self.session_id, "vkconfig.json")
			self.vk.login(self.settings["vk"]["user"], self.settings["vk"]["password"], token=self.settings["vk"]["token"], alt_token=self.settings["vk"]["use_alternative_tokens"], filename=config_filename)
			self.settings["vk"]["token"] = self.vk.session_object.token["access_token"]
			self.settings.write()
			self.logged = True
			self.get_my_data()
		except ValueError:
			self.settings["vk"]["user"] = ""
			self.settings["vk"]["password"] = ""
			self.settings.write()
			pub.sendMessage("authorisation-failed")

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
			if show_nextpage == False:
				self.process_usernames(data)
#			else:
#				print data.keys(), len(data["items"]), data["next_from"]
			num = self.order_buffer(name, data["items"], show_nextpage)
			log.debug("Keys of the returned data for debug purposes: %r" % (list(data.keys()),))
			if "next_from" in data:
				self.db[name]["cursor"] = data["next_from"]
			return num

	def get_page(self, name="", show_nextpage=False, endpoint="", *args, **kwargs):
		data = None
		if "audio" in endpoint and self.settings["vk"]["use_alternative_tokens"]:
			log.info("Using alternative audio methods.")
			c = self.vk.client_audio
		else:
			c = self.vk.client
		if "parent_endpoint" in kwargs:
			p = kwargs["parent_endpoint"]
			if "audio" in p and self.settings["vk"]["use_alternative_tokens"]:
				log.info("Using alternative audio methods.")
				c = self.vk.client_audio
			kwargs.pop("parent_endpoint")
		try:
			p = getattr(c, p)
		except AttributeError:
			p = c
		log.debug("Calling endpoint %s with params %r" % (p, kwargs,))
		data = getattr(p, endpoint)(*args, **kwargs)
		if data != None:
			if type(data) == dict:
				num = self.order_buffer(name, data["items"], show_nextpage)
				if len(data["items"]) > 0 and "first_name" in data["items"][0]:
					data2 = {"profiles": [], "groups": []}
					for i in data["items"]:
						data2["profiles"].append(i)
					self.process_usernames(data2)
				if "profiles" in data and "groups" in data:
					self.process_usernames(data)
			else:
				num = self.order_buffer(name, data, show_nextpage)
			return num

	def get_messages(self, name="", *args, **kwargs):
		data = self.vk.client.messages.getHistory(*args, **kwargs)
		data["items"].reverse()
		if data != None:
			num = self.order_buffer(name, data["items"], False)
			return num

	def get_user_name(self, user_id, case_name="gen"):
		if user_id > 0:
			warnings.warn("Call to a deprecated function. Use get_user instead.")
			if user_id in self.db["users"]:
				if case_name in self.db["users"][user_id]:
					return self.db["users"][user_id][case_name]
				else:
#					print(self.get_user(user_id, key="usuario1"))
					return self.db["users"][user_id]["first_name_nom"]+" "+self.db["users"][user_id]["last_name_nom"]
			else:
				self.get_users(user_ids=user_id)
				return self.get_user_name(user_id)
		else:
			if abs(user_id) in self.db["groups"]:
				return self.db["groups"][abs(user_id)]["nom"]
			else:
				return "no specified community"

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
		else:
			if abs(user_id) in self.db["groups"]:
				user_data = {}
				user_fields = "nom, gen, ins, dat, abl, acc".split(", ")
				for i in user_fields:
					k = "{key}_{case}".format(key=key, case=i)
					v = self.db["groups"][abs(user_id)][i]
					user_data[k] = v
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