# -*- coding: utf-8 -*-
""" A profile viewer and editor for VK user objects."""
import cStringIO
import webbrowser
import logging
import arrow
import requests
import languageHandler
import widgetUtils
import output
import wx
from wxUI.dialogs import urlList, profiles
from sessionmanager import utils

log = logging.getLogger("controller.profiles")

class userProfile(object):
	""" Main controller to view an user profile. This controller will retrieve needed data from the VK website and display it appropiately."""

	def __init__(self, session, user_id):
		""" Default constructor:
		@session vk.session: The main session object, capable of calling VK methods.
		@user_id integer: User ID to retrieve information of.
		At the current time, only users (and not communities) are supported.
		"""
		# self.person will hold a reference to the user object when retrieved from VK.
		self.person = None
		self.session = session
		self.user_id = user_id
		self.dialog = profiles.userProfile(title=_(u"Profile"))
		self.dialog.create_controls("main_info")
		self.dialog.realice()
		self.get_basic_information()
		if self.person != None:
			self.dialog.get_response()

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
			return output.speak(_(u"Information for groups is not supported, yet."))
		person = person[0]
		# toDo: remove this print when I will be done with creation of profile viewer logic.
		print(person)
		# From this part we will format data from VK so users will see it in the GUI control.
		# Format full name.
		n = u"{0} {1}".format(person["first_name"], person["last_name"])
		# Format birthdate.
		if person.has_key("bdate") and person["bdate"] != "":
			self.dialog.main_info.enable("bdate")
			# VK can display dd.mm or dd.mm.yyyy birthdates. So let's compare the string lenght to handle both cases accordingly.
			if len(person["bdate"]) <= 5: # dd.mm
				d = arrow.get(person["bdate"], "D.M")
				self.dialog.main_info.set("bdate", d.format(_(u"MMMM D"), locale=languageHandler.getLanguage()))
			else: # mm.dd.yyyy
				d = arrow.get(person["bdate"], "D.M.YYYY")
				self.dialog.main_info.set("bdate", d.format(_(u"MMMM D, YYYY"), locale=languageHandler.getLanguage()))
		# Format current city and home town
		city = ""
		if person.has_key("home_town") and person["home_town"] != "":
			home_town = person["home_town"]
			self.dialog.main_info.enable("home_town")
			self.dialog.main_info.set("home_town", home_town)
		if person.has_key("city") and len(person["city"]) > 0:
			city = person["city"]["title"]
		if person.has_key("country") and person["country"] != "":
			if city != "":
				city = city+u", {0}".format(person["country"]["title"])
			else:
				city = person["country"]["title"]
			self.dialog.main_info.enable("city")
			self.dialog.main_info.set("city", city)
		self.dialog.main_info.set("name", n)
		self.dialog.SetTitle(_(u"{name}'s profile").format(name=n,))
		# Format website (or websites, if there are multiple of them).
		if person.has_key("site") and person["site"] != "":
			self.dialog.main_info.enable("website")
			self.dialog.main_info.set("website", person["site"])
			self.dialog.main_info.enable("go_site")
			widgetUtils.connect_event(self.dialog.main_info.go_site, widgetUtils.BUTTON_PRESSED, self.visit_website)
		# Format status message.
		if person.has_key("status") and person["status"] != "":
			self.dialog.main_info.enable("status")
			self.dialog.main_info.set("status", person["status"])
		# Format occupation.
		# toDo: Research in this field is needed. Sometimes it returns university information even if users have active work places.
		if person.has_key("occupation") and person["occupation"] != None:
			if person["occupation"]["type"] == "work": c1 = _(u"Work ")
			elif person["occupation"]["type"] == "school": c1 = _(u"Student ")
			elif person["occupation"]["type"] == "university": c1 = _(u"Student ")
			if person["occupation"].has_key("name") and person["occupation"]["name"] != "":
				c2 = _(u"In {0}").format(person["occupation"]["name"],)
			else:
				c2 = ""
			self.dialog.main_info.enable("occupation")
			self.dialog.main_info.set("occupation", c1+c2)
		# format relationship status.
		# ToDo: When dating someone, the button associated to the information should point to the profile of the user.
		if person.has_key("relation") and person["relation"] != 0:
			if person["relation"] == 1:
				r =  _(u"Single")
			elif person["relation"] == 2:
				if person.has_key("relation_partner"):
					r = _(u"Dating with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
				else:
					r = _(u"Dating")
			elif person["relation"] == 3:
				r = _(u"Engaged with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
			elif person["relation"] == 4:
				r = _(u"Married with {0} {1}").format(person["relation_partner"]["first_name"], person["relation_partner"]["last_name"])
			elif person["relation"] == 5:
				r = _(u"It's complicated")
			elif person["relation"] == 6:
				r = _(u"Actively searching")
			elif person["relation"] == 7:
				r = _(u"In love")
			self.dialog.main_info.enable("relation")
			self.dialog.main_info.relation.SetLabel(_(u"Relationship: ")+r)
		# format last seen.
		if person.has_key("last_seen") and person["last_seen"] != False:
			original_date = arrow.get(person["last_seen"]["time"])
			# Translators: This is the date of last seen
			last_seen = _(u"{0}").format(original_date.humanize(locale=languageHandler.getLanguage()),)
			self.dialog.main_info.enable("last_seen")
			self.dialog.main_info.set("last_seen", last_seen)
		self.person = person
		# Adds photo to the dialog.
		# ToDo: Need to ask if this has a visible effect in the dialog.
		if person.has_key("photo_200_orig"):
			img = requests.get(person["photo_200_orig"])
			image = wx.Image(stream=cStringIO.StringIO(requests.get(person["photo_200_orig"]).content))
			try:
				self.dialog.image.SetBitmap(wx.Bitmap(image))
			except ValueError:
				return
		self.dialog.panel.Layout()

	def visit_website(self, *args, **kwargs):
		""" Allows to visit an user's website. """
		text = self.person["site"]
		# Let's search for URLS with a regexp, as there are users with multiple websites in their profiles.
		urls = utils.find_urls_in_text(text)
		if len(urls) == 0:
			output.speak(_(u"No URL addresses were detected."))
			return
		elif len(urls) == 1:
			selected_url = urls[0]
		else:
			dialog = urlList.urlList()
			dialog.populate_list(urls)
			if dialog.get_response() != widgetUtils.OK:
				return
			selected_url = urls[dialog.get_item()]
		output.speak(_(u"Opening URL..."))
		webbrowser.open_new_tab(selected_url)