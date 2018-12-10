# -*- coding: utf-8 -*-
import logging
import languageHandler
import paths
import vkSessionHandler
import sound
from config_utils import Configuration, ConfigurationResetException
from pubsub import pub
from vk_api.exceptions import LoginRequired, VkApiError

log = logging.getLogger("session")

sessions = {}

# Saves possible set of identifier keys for VK'S data types
# see https://vk.com/dev/datatypes for more information.
# I've added the Date identifier (this is a field in unix time format), for special objects (like friendship indicators) because these objects doesn't have an own identifier.
identifiers = ["aid", "gid", "uid", "pid", "id", "post_id", "nid", "date"]

def find_item(list, item):
	""" Finds an item in a list  by taking an identifier"""
	# determines the kind of identifier that we are using
	global identifiers
	identifier = None
	for i in identifiers:
		if item.has_key(i):
			identifier =   i
			break
	if identifier == None:
		# if there are objects that can't be processed by lack of identifier, let's print  keys for finding one.
		log.exception("Can't find an identifier for the following object: %r" % (item.keys(),))
	for i in list:
		if i.has_key(identifier) and i[identifier] == item[identifier]:
			return True
	return False

class vkSession(object):

	def order_buffer(self, name, data, show_nextpage):

		""" Put new items on the local database. Useful for cursored buffers
		name str: The name for the buffer stored in the dictionary.
		data list: A list with items and some information about cursors.
		returns the number of items that has been added in this execution"""
		first_addition = False
		num = 0
		if self.db.has_key(name) == False:
			self.db[name] = {}
			self.db[name]["items"] = []
			first_addition = True
		for i in data:
			if i.has_key("type") and (i["type"] == "wall_photo" or i["type"] == "photo_tag" or i["type"] == "photo"):
				log.debug("Skipping unsupported item... %r" % (i,))
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
		self.settings = Configuration(paths.config_path(file_), paths.app_path("session.defaults"))
		self.soundplayer = sound.soundSystem(self.settings["sound"])
#  except:
#   log.exception("The session configuration has failed.")

	def login(self):
		try:
			self.vk.login(self.settings["vk"]["user"], self.settings["vk"]["password"], filename=paths.config_path(self.session_id+"/vkconfig.json"))
			self.settings["vk"]["token"] = self.vk.client._session.access_token
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
		if show_nextpage == True and self.db[name].has_key("cursor"):
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
			log.debug("Keys of the returned data for debug purposes: %r" % (data.keys(),))
			if data.has_key("next_from"):
				self.db[name]["cursor"] = data["next_from"]
			return num

	def get_page(self, name="", show_nextpage=False, endpoint="", *args, **kwargs):
		data = None
		if "audio" in endpoint:
			c = self.vk.client_audio
		else:
			c = self.vk.client
		if kwargs.has_key("parent_endpoint"):
			p = kwargs["parent_endpoint"]
			if "audio" in p:
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
				if len(data["items"]) > 0 and data["items"][0].has_key("first_name"):
					data2 = {"profiles": [], "groups": []}
					for i in data["items"]:
						data2["profiles"].append(i)
					self.process_usernames(data2)
				if data.has_key("profiles") and data.has_key("groups"):
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
			if self.db["users"].has_key(user_id):
				if self.db["users"][user_id].has_key(case_name):
					return self.db["users"][user_id][case_name]
				else:
					return self.db["users"][user_id]["nom"]
			else:
				return "no specified user"
		else:
			if self.db["groups"].has_key(abs(user_id)):
				return self.db["groups"][abs(user_id)]["nom"]
			else:
				return "no specified community"

	def get_users(self, user_ids=None, group_ids=None):
		log.debug("Getting user information from the VK servers")
		if user_ids != None:
			u = self.vk.client.users.get(user_ids=user_ids, fields="uid, first_name, last_name")
			for i in u:
				self.db["users"][i["id"]] = u"{0} {1}".format(i["first_name"], i["last_name"])
		if group_ids != None:
			g = self.vk.client.groups.getById(group_ids=group_ids, fields="name")
			for i in g:
				self.db["groups"][i["id"]] = i["name"]

	def process_usernames(self, data):
		""" processes user IDS and saves them in a local storage system.
		Every function wich needs to convert from an ID to user or community name will have to call the get_user_name function in this session object.
		Every function that needs to save a set ot user ids for a future use needs to pass a data dictionary with a profiles key being a list of user objects.
		For russian, it gets the genitive case of  every name for future use."""
		log.debug("Adding usernames to the local database...")
		ids = ""
		for i in data["profiles"]:
			if self.db["users"].has_key(i["id"]) == False:
				self.db["users"][i["id"]] = dict(nom=u"{0} {1}".format(i["first_name"], i["last_name"]))
				ids = ids + "{0},".format(i["id"],)
		gids = ""
		for i in data["groups"]:
			self.db["groups"][i["id"]] = dict(nom=i["name"])
			gids = "{0},".format(i["id"],)
		if not "ru" in languageHandler.getLanguage():
			return
		if ids != "":
			users_genitive = self.vk.client.users.get(user_ids=ids, fields="first_name, last_name", name_case="gen")
			users_instrumental = self.vk.client.users.get(user_ids=ids, fields="first_name, last_name", name_case="ins")
			for i in users_genitive:
				if self.db["users"].has_key(i["id"]):
					self.db["users"][i["id"]]["gen"] = u"{0} {1}".format(i["first_name"], i["last_name"])
			for i in users_instrumental:
				if self.db["users"].has_key(i["id"]):
					self.db["users"][i["id"]]["ins"] = u"{0} {1}".format(i["first_name"], i["last_name"])

	def get_my_data(self):
		log.debug("Getting user identifier...")
		user = self.vk.client.users.get(fields="uid, first_name, last_name")
		self.user_id = user[0]["id"]
