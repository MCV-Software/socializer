# -*- coding: utf-8 -*-
import time
import arrow
import languageHandler
import paths
import vkSessionHandler
import logging
import utils
from config_utils import Configuration, ConfigurationResetException
log = logging.getLogger("vk.session")

sessions = {}

# Saves possible set of identifier keys for VK'S data types
# see https://vk.com/dev/datatypes for more information.
# I've added the Date identifier (this is a field in unix time format), for special objects (like friendships indicators) because these objects doesn't have an own identifier.
identifiers = ["aid", "gid", "uid", "pid", "id", "post_id", "nid", "date"]

def find_item(list, item):
	""" Finds an item in a list  by taking an identifier"""
	# determines the kind of identifier that we are using
	global identifiers
	identifier = None
	for i in identifiers:
		if item.has_key(i):
			identifier = i
	if identifier == None:
		# if there are objects that can't be processed by lack of identifier, let's print  keys for finding one.
		print item.keys()
	for i in list:
		if i.has_key(identifier) and i[identifier] == item[identifier]:
			return True
	return False

def add_attachment(attachment):
	""" Adds information about the attachment files in posts. It only adds the text, I mean, no attachment file is added here.
	This will produce a result like 'Title of a web page: http://url.xxx', etc."""
	msg = u""
	if attachment["type"] == "link":
		msg = u"{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
	elif attachment["type"] == "photo":
		msg = attachment["photo"]["text"]
		if msg == "":
			return "photo with no description available"
	elif attachment["type"] == "video":
		msg = u"video: {0}".format(attachment["video"]["title"],)
	return msg

def add_text(status):
	""" This shorts the text to 140 characters for displaying it in the list control."""
	message = ""
	if status.has_key("text"):
		if len(status["text"]) < 140:
			message = status["text"]
		else:
			message = status["text"][:139]
	return message

def compose_new(status, session):
	""" This method is used to compose an item of the news feed."""
	user = session.get_user_name(status["source_id"])
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.getLanguage())
	if status["type"] == "post":
		message += add_text(status)
		if status.has_key("attachment") and len(status["attachment"]) > 0:
			message += add_attachment(status["attachment"])
		if message == "":
			message = "no description available"
	elif status["type"] == "audio":
		message = _(u"{0} has posted an audio: {1}").format(user, u", ".join(compose_audio(status["audio"][1], session)),)
	elif status["type"] == "friend":
		msg_users = u""
		for i in status["friends"][1:]:
			msg_users = msg_users + u"{0}, ".format(session.get_user_name(i["uid"]))
		message = _(u"{0} hadded friends: {1}").format(user, msg_users)
	else:
		if status["type"] != "post": print status["type"]
	return [user, message, created_at]

def compose_status(status, session):
	user = session.get_user_name(status["from_id"])
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.getLanguage())
	if status["post_type"] == "post":
		message += add_text(status)
	if status.has_key("attachment") and len(status["attachment"]) > 0:
		message += add_attachment(status["attachment"])
		if message == "":
			message = "no description available"
	return [user, message, created_at]

def compose_audio(audio, session):
	if audio == False: return [_(u"Audio removed from library"), "", ""]
	return [audio["title"], audio["artist"], utils.seconds_to_string(audio["duration"])]

class vkSession(object):

	def order_buffer(self, name, data, field):

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
			if i.has_key("type") and i["type"] == "wall_photo": continue
			if find_item(self.db[name]["items"], i) == False:
#			if i not in self.db[name]["items"]:
				if first_addition:
					if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].append(i)
					else: self.db[name]["items"].insert(0, i)
				else:
					if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].insert(0, i)
					else: self.db[name]["items"].append(i)
				num = num+1

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
#  except:
#   log.exception("The session configuration has failed.")

	def login(self):
		""" Login  using  credentials from settings.
		if the user account isn't authorised, it'll call self.authorise() before login.
		If the access_token has expired, it will call authorise() too, for getting a new access token."""

		if self.settings["vk"]["token"] != None:
			result = self.vk.login_access_token(self.settings["vk"]["token"])
			self.logged = True
			log.debug("Logged.")
			if result == False:
				self.authorise()
		else:
			self.authorise()
		self.get_my_data()

	def authorise(self):
		self.vk.login(self.settings["vk"]["user"], self.settings["vk"]["password"])
		self.settings["vk"]["token"] = self.vk.client._session.access_token
		self.settings.write()

	def post_wall_status(self, message, *args, **kwargs):
		""" Sends a post to an user, group or community wall."""
		response = self.vk.client.wall.post(message=message, *args, **kwargs)

	def get_newsfeed(self, name="newsfeed", no_next=True, endpoint="", *args, **kwargs):
		data = getattr(self.vk.client.newsfeed, "get")(*args, **kwargs)
		if data != None:
			self.process_usernames(data)
			num = self.order_buffer(name, data["items"][:-1], "post_id")
			return num

	def get_page(self, name="", no_next=True, endpoint="", *args, **kwargs):
		data = None
		full_list = False
		if kwargs.has_key("parent_endpoint"):
			p = kwargs["parent_endpoint"]
			kwargs.pop("parent_endpoint")
		if kwargs.has_key("full_list"):
			print kwargs
			full_list = True
			kwargs.pop("full_list")
		if kwargs.has_key("identifier"):
			identifier = kwargs["identifier"]
			kwargs.pop("identifier")
		p = getattr(self.vk.client, p)
		data = getattr(p, endpoint)(*args, **kwargs)
#			print data
		if data != None:
#			try:
			if full_list == False:
				num = self.order_buffer(name, data[1:], identifier)
			else:
				num = self.order_buffer(name, data, identifier)
#			except:
#				num = self.order_buffer(name, data["items"][:-1])
			ids = ""
			for i in data[1:]:
				if i.has_key("from_id"):
					if str(i["from_id"]) not in ids: ids += "{0},".format(i["from_id"])
			self.get_users(ids)
			return num

	def get_user_name(self, user_id):
		if user_id > 0:
			if self.db["users"].has_key(user_id):
				return self.db["users"][user_id]
			else:
				return "no specified user"
		else:
			if self.db["groups"].has_key(abs(user_id)):
				return self.db["groups"][abs(user_id)]
			else:
				return "no specified community"

	def get_users(self, user_ids=None, group_ids=None):
		if user_ids != None:
			u = self.vk.client.users.get(user_ids=user_ids, fields="uid, first_name, last_name")
			for i in u:
				self.db["users"][i["uid"]] = u"{0} {1}".format(i["first_name"], i["last_name"])
		if group_ids != None:
			g = self.vk.client.groups.getById(group_ids=group_ids, fields="name")
			for i in g:
				self.db["groups"][i["gid"]] = i["name"]

	def process_usernames(self, data):
		for i in data["profiles"]:
			self.db["users"][i["uid"]] = u"{0} {1}".format(i["first_name"], i["last_name"])
		for i in data["groups"]:
			self.db["groups"][i["gid"]] = i["name"]

	def get_my_data(self):
		self.user_id = self.vk.client.users.get(fields="uid")[0]["uid"]