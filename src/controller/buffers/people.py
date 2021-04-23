# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
import time
import logging
import webbrowser
import arrow
import wx
import presenters
import views
import interactors
import languageHandler
import widgetUtils
from pubsub import pub
from wxUI.tabs import people
from wxUI.dialogs import timeline
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.friends")

class peopleBuffer(wallBuffer):

	def post(self, *args, **kwargs):
		user = self.get_post()
		if "can_post" not in user: # retrieve data if not present in the object.
			user = self.session.vk.client.users.get(user_ids=user["id"], fields="can_post")[0]
		if user.get("can_post") == True:
			user_str = self.session.get_user(user["id"], key="user1")
			title = _("Post to {user1_nom}'s wall").format(**user_str)
			p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=title, message="", text=""))
			if hasattr(p, "text") or hasattr(p, "privacy"):
				post_arguments=dict(privacy=p.privacy, message=p.text, owner_id=user["id"])
				attachments = []
				if hasattr(p, "attachments"):
					attachments = p.attachments
				call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="post", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)

	def create_tab(self, parent):
		self.tab = people.peopleTab(parent)
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
		if post.get("can_post") == True:
			self.tab.post.Enable(True)
		else:
			self.tab.post.Enable(False)
		# Check if we are allowed to contact people. this might be false for communitiy members.
		if post.get("can_write_private_message") == True:
			self.tab.new_chat.Enable(True)
		else:
			self.tab.new_chat.Enable(False)
		print(post)
		if ("last_seen" in post) == False: return
		original_date = arrow.get(post["last_seen"]["time"])
		now = arrow.now()
		original_date.to(now.tzinfo)
		diffdate = now-original_date
		if diffdate.days == 0 and diffdate.seconds <= 360:
			online_status = _("Online")
		else:
		# Translators: This is the date of last seen
			online_status = _("Last seen {0}").format(original_date.humanize(locale=languageHandler.curLang[:2]),)
		self.tab.list.list.SetItem(self.tab.list.get_selected(), 1, online_status)

	def open_timeline(self, *args, **kwargs):
		user = self.get_post()
		if user == None:
			return
		a = timeline.timelineDialog([self.session.get_user(user["id"])["user1_gen"]], show_selector=False)
		if a.get_response() == widgetUtils.OK:
			buffer_type = a.get_buffer_type()
			user_id = user["id"]
			pub.sendMessage("create-timeline", user_id=user_id, buffer_type=buffer_type)

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
			widgetUtils.connect_event(m, widgetUtils.MENU, self.decline_friendship, menuitem=m.decline)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.block_person, menuitem=m.block)
		# It is not allowed to send messages to people who is not your friends, so let's disable it if we're in a pending or outgoing requests buffer.
		if "friend_requests" in self.name:
			m.message.Enable(False)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.new_chat, menuitem=m.message)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_timeline, menuitem=m.timeline)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
		widgetUtils.connect_event(m, widgetUtils.MENU, self.open_in_browser, menuitem=m.open_in_browser)
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
			msg = _("You've removed {user1_nom} from your friends.").format(**user,)
		pub.sendMessage("notify", message=msg)
		self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
		self.tab.list.remove_item(self.tab.list.get_selected())

	def block_person(self, *args, **kwargs):
		person = self.get_post()
		if person == None:
			return
		user = self.session.get_user(person["id"])
		question = commonMessages.block_person(user)
		if question == widgetUtils.NO:
			return
		result = self.session.vk.client.account.ban(owner_id=person["id"])
		if result == 1:
			msg = _("You've blocked {user1_nom} from your friends.").format(**user,)
			pub.sendMessage("notify", message=msg)
			self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
			self.tab.list.remove_item(self.tab.list.get_selected())

	def keep_as_follower(self, *args, **kwargs):
		pass

	def add_person(self, person):
		# This tracks if the user already exists here, in such case we just will update the last_seen variable
		existing = False
		for i in self.session.db[self.name]["items"]:
			if person["id"] == i["id"]:
				existing = True
				i["last_seen"]["time"] = person["last_seen"]["time"]
				break
		# Add the new user to the buffer just if it does not exists previously.
		if existing == False:
			# Ensure the user won't loose the focus after the new item is added.
			focused_item = self.tab.list.get_selected()+1
			self.session.db[self.name]["items"].insert(0, person)
			self.insert(person, True)
			# Selects back the previously focused item.
			self.tab.list.select_item(focused_item)

	def remove_person(self, user_id):
		# Make sure the user is present in the buffer, otherwise don't attempt to remove a None Value from the list.
		user = None
		focused_user = self.get_post()
		for i in self.session.db[self.name]["items"]:
			if i["id"] == user_id:
				user = i
				break
		if user != None:
			person_index = self.session.db[self.name]["items"].index(user)
			focused_item = self.tab.list.get_selected()
			self.session.db[self.name]["items"].pop(person_index)
			self.tab.list.remove_item(person_index)
			if user != focused_user:
			# Let's find the position of the previously focused user.
				focus = None
				for i in range(0, len(self.session.db[self.name]["items"])):
					if focused_user["id"] == self.session.db[self.name]["items"][i]["id"]:
						self.tab.list.select_item(i)
						return
			elif user == focused_user and person_index < self.tab.list.get_count():
				self.tab.list.select_item(person_index)
			else:
				self.tab.list.select_item(self.tab.list.get_count()-1)

	def get_friend(self, user_id):
		for i in self.session.db["friends_"]["items"]:
			if i["id"] == user_id:
				return i
			log.exception("Getting user manually...")
			user = self.session.vk.client.users.get(user_ids=event.user_id, fields="last_seen")[0]
			return user

	def update_online(self):
		online_users = self.session.vk.client.friends.getOnline()
		now = time.time()
		for i in self.session.db[self.name]["items"]:
			if i["id"] in online_users:
				i["last_seen"]["time"] = now
			else:
				log.exception("Removing an user from online status manually... %r" % (i))
				self.remove_person(i["id"])

	def open_in_browser(self, *args, **kwargs):
		post = self.get_post()
		if post == None:
			return
		url = "https://vk.com/id{user_id}".format(user_id=post["id"])
		webbrowser.open_new_tab(url)