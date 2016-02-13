# -*- coding: utf-8 -*-
import arrow
import languageHandler
import paths
import vkSessionHandler
import logging
import utils
from config_utils import Configuration, ConfigurationResetException
log = logging.getLogger("vk.session")

sessions = {}

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
		message = u"{0} has posted an audio: {1}".format(user, u", ".join(compose_audio(status["audio"][1], session)),)
	elif status["type"] == "friend":
		ids = ""
		for i in status["friends"][1:]:
			ids = ids + "{0}, ".format(i["uid"])
		users = session.vk.client.users.get(user_ids=ids, fields="uid, first_name, last_name")
		msg_users = u""
		for i in users:
			msg_users = msg_users + u"{0} {1}, ".format(i["first_name"], i["last_name"])
		message = u"{0} hadded friends: {1}".format(user, msg_users)
	else:
		if status["type"] != "post": print status["type"]
	return [user, message, created_at]

def compose_status(status, session):
#	print status.keys()
	user = session.get_user_name(status["from_id"])
	message = ""
#	user = status["copy_owner_id"]
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.getLanguage())
#	created_at = str(status["date"])
	if status["post_type"] == "post":
		message += add_text(status)
	if status.has_key("attachment") and len(status["attachment"]) > 0:
		message += add_attachment(status["attachment"])
		if message == "":
			message = "no description available"
	return [user, message, created_at]

def compose_audio(audio, session):
#	print audio
	return [audio["title"], audio["artist"], utils.seconds_to_string(audio["duration"])]

class vkSession(object):

	def order_buffer(self, name, data, field):

		""" Put the new items on the local database. Useful for cursored buffers
		name str: The name for the buffer stored in the dictionary.
		data list: A list with items and some information about cursors.
		returns the number of items that has been added in this execution"""

		num = 0
		if self.db.has_key(name) == False:
			self.db[name] = {}
			self.db[name]["items"] = []
		for i in data:
#			print i.keys()
#			print i.keys()
#			print i["type"]
#			if i.has_key(field) and find_item(i[field], self.db[name]["items"], field) == None:
			if i.has_key("type") and i["type"] == "wall_photo": continue
			if i not in self.db[name]["items"]:
				if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].append(i)
				else: self.db[name]["items"].insert(0, i)
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
		if the user account isn't authorised, it needs to call self.authorise() before login."""

		if self.settings["vk"]["token"] != None:
			self.vk.login_access_token(self.settings["vk"]["token"])
			self.logged = True
			log.debug("Logged.")
		else:
			self.logged = False
			raise Exceptions.RequireCredentialsSessionError

	def authorise(self):
		if self.logged == True:
			raise Exceptions.AlreadyAuthorisedError("The authorisation process is not needed at this time.")
		else:
			self.vk.login(self.settings["vk"]["user"], self.settings["vk"]["password"])
			self.settings["vk"]["token"] = self.vk.client._session.access_token

	def post_wall_status(self, message, *args, **kwargs):
		response = self.vk.client.wall.post(message=message, *args, **kwargs)
#		print response

	def get_newsfeed(self, name="newsfeed", no_next=True, endpoint="", *args, **kwargs):
		data = getattr(self.vk.client.newsfeed, "get")(*args, **kwargs)
#			print data
		if data != None:
#			try:
#			num = self.order_buffer(name, data[1:])
#			except:
			num = self.order_buffer(name, data["items"][:-1], "post_id")
			ids = ""
			gids = ""
			for i in data["items"][:-1]:
				if i.has_key("source_id"):
					if i["source_id"] > 0:
						if str(i["source_id"]) not in ids: ids += "{0},".format(i["source_id"])
					else:
						if str(i["source_id"]) not in gids: gids += "{0},".format(abs(i["source_id"]))
			self.get_users(ids, gids)
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
