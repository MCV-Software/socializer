# -*- coding: utf-8 -*-
""" A profile viewer and editor for VK user objects."""
from __future__ import unicode_literals
import webbrowser
import logging
import arrow
import requests
import languageHandler
import output
from mysc.thread_utils import call_threaded
from sessionmanager import utils
from . import base

log = logging.getLogger("controller.profiles")

class userProfilePresenter(base.basePresenter):

	def __init__(self, session, user_id, view, interactor):
		""" Default constructor:
		@session vk.session: The main session object, capable of calling VK methods.
		@user_id integer: User ID to retrieve information of.
		At the current time, only users (and not communities) are supported.
		"""
		super(userProfilePresenter, self).__init__(view=view, interactor=interactor, modulename="user_profile")
		# self.person will hold a reference to the user object when retrieved from VK.
		self.person = None
		self.session = session
		self.user_id = user_id
		# Get information in a threaded way here.
		# Note: We do not handle any race condition here because due to the presenter only sending pubsub messages,
		# Nothing happens if the pubsub send messages to the interactor after the latter has been destroyed.
		# Pubsub messages are just skipped if there are no listeners for them.
		call_threaded(self.get_basic_information)
		self.run()

	def get_basic_information(self):
		""" Gets and inserts basic user information.
		See https://vk.com/dev/users.get"""
		# List of fields (information) to retrieve. For a list of fields available for user objects,
		# see https://vk.com/dev/fields
		fields = "first_name, last_name, bdate, city, country, home_town, photo_200_orig, online,  site,  status, last_seen, occupation, relation, relatives, personal, connections, activities, interests, music, movies, tv, books, games, about, quotes, can_write_private_message"
		# ToDo: this method supports multiple user IDS, I'm not sure if this may be of any help for profile viewer.
		person = self.session.vk.client.users.get(user_ids=self.user_id, fields=fields)
		# If VK does not return anything it is very likely we have found a community.
		if len(person) == 0:
			return output.speak(_("Information for groups is not supported, yet."))
		person = person[0]
		# toDo: remove this print when I will be done with creation of profile viewer logic.
#		print(person)
		# From this part we will format data from VK so users will see it in the GUI control.
		# Format full name.
		n = "{0} {1}".format(person["first_name"], person["last_name"])
		# Format birthdate.
		if "bdate" in person and person["bdate"] != "":
			self.send_message("enable_control", tab="main_info", control="bdate")
			# VK can display dd.mm or dd.mm.yyyy birthdates. So let's compare the string lenght to handle both cases accordingly.
			if len(person["bdate"]) <= 5: # dd.mm
				d = arrow.get(person["bdate"], "D.M")
				self.send_message("set", tab="main_info", control="bdate", value=d.format(_("MMMM D"), locale=languageHandler.curLang[:2]))
			else: # mm.dd.yyyy
				d = arrow.get(person["bdate"], "D.M.YYYY")
				self.send_message("set", tab="main_info", control="bdate", value=d.format(_("MMMM D, YYYY"), locale=languageHandler.curLang[:2]))
		# Format current city and home town
		city = ""
		if "home_town" in person and person["home_town"] != "":
			home_town = person["home_town"]
			self.send_message("enable_control", tab="main_info", control="home_town")
			self.send_message("set", tab="main_info", control="home_town", value=home_town)
		if "city" in person and len(person["city"]) > 0:
			city = person["city"]["title"]
		if "country" in person and person["country"] != "":
			if city != "":
				city = city+", {0}".format(person["country"]["title"])
			else:
				city = person["country"]["title"]
			self.send_message("enable_control", tab="main_info", control="city")
			self.send_message("set", tab="main_info", control="city", value=city)
		self.send_message("set", tab="main_info", control="name", value=n)
		# Format title
		user = self.session.get_user(person["id"])
		self.send_message("set_title", value=_("{user1_nom}'s profile").format(**user))
		# Format website (or websites, if there are multiple of them).
		if "site" in person and person["site"] != "":
			self.send_message("enable_control", tab="main_info", control="website")
			self.send_message("set", tab="main_info", control="website", value=person["site"])
			self.send_message("enable_control", tab="main_info", control="go_site")
		# Format status message.
		if "status" in person and person["status"] != "":
			self.send_message("enable_control", tab="main_info", control="status")
			self.send_message("set", tab="main_info", control="status", value=person["status"])
		# Format occupation.
		# toDo: Research in this field is needed. Sometimes it returns university information even if users have active work places.
		if "occupation" in person and person["occupation"] != None:
			if person["occupation"]["type"] == "work": c1 = _("Work ")
			elif person["occupation"]["type"] == "school": c1 = _("Student ")
			elif person["occupation"]["type"] == "university": c1 = _("Student ")
			if "name" in person["occupation"] and person["occupation"]["name"] != "":
				c2 = _("In {0}").format(person["occupation"]["name"],)
			else:
				c2 = ""
			self.send_message("enable_control", tab="main_info", control="occupation")
			self.send_message("set", tab="main_info", control="occupation", value=c1+c2)
		# format relationship status.
		# ToDo: When dating someone, the button associated to the information should point to the profile of the user.
		if "relation" in person and person["relation"] != 0:
			if person["relation"] == 1:
				r =  _("Single")
			elif person["relation"] == 2:
				if "relation_partner" in person:
					r = _("Dating with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
				else:
					r = _("Dating")
			elif person["relation"] == 3:
				r = _("Engaged with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
			elif person["relation"] == 4:
				if "relation_partner" in person:
					r = _("Married to {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
				else:
					r = _("Married")
			elif person["relation"] == 5:
				r = _("It's complicated")
			elif person["relation"] == 6:
				r = _("Actively searching")
			elif person["relation"] == 7:
				r = _("In love")
			self.send_message("enable_control", tab="main_info", control="relation")
			self.send_message("set_label", tab="main_info", control="relation", value=_("Relationship: ")+r)
		# format last seen.
		if "last_seen" in person and person["last_seen"] != False:
			original_date = arrow.get(person["last_seen"]["time"])
			# Translators: This is the date of last seen
			last_seen = _("{0}").format(original_date.humanize(locale=languageHandler.curLang[:2]),)
			self.send_message("enable_control", tab="main_info", control="last_seen")
			self.send_message("set", tab="main_info", control="last_seen", value=last_seen)
		self.person = person
		# Adds photo to the dialog.
		# ToDo: Need to ask if this has a visible effect in the dialog.
		if "photo_200_orig" in person:
			img = requests.get(person["photo_200_orig"])
			self.send_message("load_image", image=requests.get(person["photo_200_orig"]))
		output.speak(_("Profile loaded"))

	def get_urls(self, *args, **kwargs):
		""" Allows to visit an user's website. """
		text = self.person["site"]
		# Let's search for URLS with a regexp, as there are users with multiple websites in their profiles.
		urls = utils.find_urls_in_text(text)
		if len(urls) == 0:
			output.speak(_("No URL addresses were detected."))
			return
		return urls

	def visit_url(self, url):
		output.speak(_("Opening URL..."))
		webbrowser.open_new_tab(url)