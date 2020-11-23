# -*- coding: utf-8 -*-
""" this module contains everything used to render different kind of posts (posts in the home buffer,
Chat messages, audios, videos, photos, comments in posts, etc)"""
import arrow
import languageHandler
import logging
from update.utils import convert_bytes
from . utils import seconds_to_string, clean_text

log = logging.getLogger(__file__)

### Some util funtions

def extract_attachment(attachment):
	""" Adds information about attachment files in posts. It only adds the text, I mean, no attachment file is added here.
	This will produce a result like:
	'website: http://url.com'.
	'photo: A forest'."""
	msg = ""
	if attachment["type"] == "link":
		msg = "{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
	elif attachment["type"] == "photo":
		msg = attachment["photo"]["text"]
		if msg == "":
			return _("photo with no description available")
	elif attachment["type"] == "video":
		msg = _("video: {0}").format(attachment["video"]["title"],)
	return msg

def short_text(status):
	""" This shorts the text to 140 characters for displaying it in the list control of buffers."""
	message = ""
	# copy_story indicates that the post is a shared repost.
	if "copy_history" in status:
		txt = status["copy_history"][0]["text"]
	else:
		txt = status["text"]
	if len(txt) < 140:
		message = clean_text(txt)
	else:
		message = clean_text(txt[:139])
	return message

def clean_audio(audio):
	""" Remove unavailable songs due to different reasons. This is used to clean the audio list when people adds audios and need to be displayed in the buffer."""
	for i in audio["items"][:]:
		if type(i) == bool:
			audio["items"].remove(i)
			audio["count"] = audio["count"] -1
	return audio

def add_attachment(attachment):
	msg = ""
	tpe = ""
	if attachment["type"] == "link":
		msg = "{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
		tpe = _("Link")
	elif attachment["type"] == "photo":
		tpe = _("Photo")
		msg = attachment["photo"]["text"]
		if msg == "":
			msg = _("no description available")
	elif attachment["type"] == "video":
		msg = "{0}".format(attachment["video"]["title"],)
		tpe = _("Video")
	elif attachment["type"] == "audio":
		msg = "{0}".format(" ".join(render_audio(attachment["audio"])))
		tpe = _("Audio")
	elif attachment["type"] == "doc":
		msg = "{0}".format(attachment["doc"]["title"])
		tpe = _("{0} file").format(attachment["doc"]["ext"])
	elif attachment["type"] == "audio_message":
		msg = "{0}".format(" ".join(render_audio_message(attachment["audio_message"])))
		tpe = _("Voice message")
	elif attachment["type"] == "poll":
		tpe = _("Poll")
		msg = attachment["poll"]["question"]
	elif attachment["type"] == "wall":
		tpe = _("Post")
		user = attachment["wall"]["from"]["name"]
		if len(attachment["wall"]["text"]) > 140:
			text = attachment["wall"]["text"][:145]+"..."
		else:
			text = attachment["wall"]["text"]
		msg = _("{user}: {post}").format(user=user, post=text)
	elif attachment["type"] == "article":
		tpe = _("Article")
		msg = "{author}: {article}".format(author=attachment["article"]["owner_name"], article=attachment["article"]["title"])
	else:
		print(attachment)
	return [tpe, msg]

### Render functions

def render_person(status, session):
	""" Render users in people buffers such as everything related to friendships or buffers created with only people.
	Example result: ["John Doe", "An hour ago"]
	Reference: https://vk.com/dev/fields"""
	# In case the user decided to not show his/her last seen information we must provide a default.
	# ToDo: Shall we indicate this with a message?
	online_status = ""
	if "last_seen" in status:
		original_date = arrow.get(status["last_seen"]["time"])
		now = arrow.now()
		original_date.to(now.tzinfo)
		diffdate = now-original_date
		if diffdate.days == 0 and diffdate.seconds <= 360:
			online_status = _("Online")
		else:
		# Translators: This is the date of last seen
			online_status = _("Last seen {0}").format(original_date.humanize(locale=languageHandler.curLang[:2]),)
	# Account suspended or deleted.
	elif ("last_seen" in status) == False and "deactivated" in status:
			online_status = _("Account deactivated")
	return ["{0} {1}".format(status["first_name"], status["last_name"]), online_status]

def render_newsfeed_item(status, session):
	""" This me☻thod is used to render an item of the news feed.
	References:
		https://vk.com/dev/newsfeed.get
		https://vk.com/dev/post_source
		https://vk.com/dev/post
	"""
	user = session.get_user(status["source_id"], key="user1")
	# See if this is a post or repost.
	if "copy_history" in status:
		# Get the second user (whose post is been shared).
		user2 = session.get_user(status["copy_history"][0]["owner_id"], key="user2")
		# Add contents of poster to the new dict, it will create both user1_nom and user2_nom.
		user2.update(user)
		user = dict(user1_nom=_("{user1_nom} has shared the {user2_nom}'s post").format(**user2))
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.curLang[:2])
	# handle status updates.
	if status["type"] == "post":
		message += short_text(status)
		if "attachment" in status and len(status["attachment"]) > 0:
			message += extract_attachment(status["attachment"])
		# If there is no message after adding text, it's because a pphoto with no description has been found.
		# so let's manually add the "no description" tag here.
		if message == "":
			message = "no description available"
	# Handle audio rendering.
	elif status["type"] == "audio" and "audio" in status:
		# removes deleted audios.
		status["audio"] = clean_audio(status["audio"])
		if status["audio"]["count"] == 1:
			data = dict(audio_file=", ".join(render_audio(status["audio"]["items"][0], session)))
			data.update(user)
			message = _("{user1_nom} has added  an audio: {audio_file}").format(**data)
		else:
			prem = ""
			for i in range(0, status["audio"]["count"]):
				composed_audio = render_audio(status["audio"]["items"][i], session)
				prem += "{0} - {1}, ".format(composed_audio[0], composed_audio[1])
			data = dict(audio_files=prem, total_audio_files=status["audio"]["count"])
			data.update(user)
			message = _("{user1_nom} has added  {total_audio_files} audios: {audio_files}").format(**data)
	# Handle audio playlists
	elif status["type"] == "audio_playlist":
		if status["audio_playlist"]["count"] == 1:
			data = dict(audio_album=status["audio_playlist"]["items"][0]["title"], audio_album_description=status["audio_playlist"]["items"][0]["description"])
			data.update(user)
			message = _("{user1_nom} has added an audio album: {audio_album}, {audio_album_description}").format(**data)
		else:
			prestring = ""
			for i in range(0, status["audio_playlist"]["count"]):
				prestring += "{0} - {1}, ".format(status["audio_playlist"]["items"][i]["title"], status["audio_playlist"]["items"][i]["description"])
			data = dict(audio_albums=prestring, total_audio_albums=status["audio_playlist"]["count"])
			data.update(user)
			message = _("{user1_nom} has added  {total_audio_albums} audio albums: {audio_albums}").format(**data)
	# handle new friends for people in the news buffer.
	elif status["type"] == "friend":
		msg_users = ""
		if "friends" in status:
			for i in status["friends"]["items"]:
				msg_users = msg_users + "{0}, ".format(session.get_user(i["user_id"])["user1_nom"])
		else:
			print(list(status.keys()))
		data = dict(friends=msg_users)
		data.update(user)
		message = _("{user1_nom} added friends: {friends}").format(**data)
	elif status["type"] == "video":
		if status["video"]["count"] == 1:
			data = dict(video=", ".join(render_video(status["video"]["items"][0], session)))
			data.update(user)
			message = _("{user1_nom} has added  a video: {video}").format(**data)
		else:
			prem = ""
			for i in range(0, status["video"]["count"]):
				composed_video = render_video(status["video"]["items"][i], session)
				prem += "{0} - {1}, ".format(composed_video[0], composed_video[1])
			data = dict(videos=prem, total_videos=status["video"]["count"])
			data.update(user)
			message = _("{user1_nom} has added  {total_videos} videos: {videos}").format(**data)
	else:
		if status["type"] != "post": print(status)
	return [user["user1_nom"], message, created_at]

def render_message(message, session):
	""" Render a message posted in a private conversation.
	Reference: https://vk.com/dev/message"""
	user = session.get_user(message["from_id"], key="user1")
	original_date = arrow.get(message["date"])
	now = arrow.now()
	original_date = original_date.to(now.tzinfo)
	# Format the date here differently depending in if this is the same day for both dates or not.
	if original_date.day == now.day:
		created_at = original_date.format(_("H:mm."), locale=languageHandler.curLang[:2])
	else:
		created_at = original_date.format(_("H:mm. dddd, MMMM D, YYYY"), locale=languageHandler.curLang[:2])
	# No idea why some messages send "text" instead "body"
	if "body" in message:
		body = message["body"]
	else:
		body = message["text"]
	data = dict(body=body, created_at=created_at)
	data.update(user)
	return ["{user1_nom}, {body} {created_at}".format(**data)]

def render_status(status, session):
	""" Render a wall post (shown in user's wall, not in newsfeed).
	Reference: https://vk.com/dev/post"""
	user = session.get_user(status["from_id"], key="user1")
	if "copy_history" in status:
		user2 = session.get_user(status["copy_history"][0]["owner_id"], key="user2")
		user2.update(user)
		user = dict(user1_nom=_("{user1_nom} has shared the {user2_nom}'s post").format(**user2))
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.curLang[:2])
	if "copy_owner_id" in status:
		user2 = session.get_user(status["copy_owner_id"], key="user2")
		user2.update(user)
		user = _("{user1_nom} has shared the {user2_nom}'s post").format(**user2)
	if status["post_type"] == "post" or status["post_type"] == "copy":
		message += short_text(status)
	if "attachment" in status and len(status["attachment"]) > 0:
		message += extract_attachment(status["attachment"])
		if message == "":
			message = "no description available"
	return [user["user1_nom"], message, created_at]

def render_audio(audio, session=None):
	""" Render audio files added to VK.
	Example result:
	["Song title", "Artist", "03:15"]
	reference: https://vk.com/dev/audio_object"""
	if audio == False: return [_("Audio removed from library"), "", ""]
	return [audio["title"], audio["artist"], seconds_to_string(audio["duration"])]

def render_video(video, session=None):
	""" Render a video file from VK.
	Example result:
	["Video title", "Video description", "01:30:28"]
	Reference: https://vk.com/dev/video_object"""
	if video == False:
		return [_("Video not available"), "", ""]
	return [video["title"], video["description"], seconds_to_string(video["duration"])]

def render_audio_message(audio_message, session=None):
	""" Render a voice message from VK
	Example result:
	["Voice message", "01:30:28"]"""
	if audio_message == False:
		return [_("Voice message not available"), "", ""]
	return [seconds_to_string(audio_message["duration"])]

def render_topic(topic, session):
	""" Render topics for a community.
	Reference: https://vk.com/dev/objects/topic"""
	user = session.get_user(topic["created_by"])
	title = topic["title"]
	comments = topic["comments"]
	last_commenter = session.get_user(topic["updated_by"])
	last_update = arrow.get(topic["updated"]).humanize(locale=languageHandler.curLang[:2])
	last_commenter.update(date=last_update)
	lastupdate = _("Last post by {user1_nom} {date}").format(**last_commenter)
	return [user["user1_nom"], title, str(comments), lastupdate]

def render_document(document, session):
	doc_types = {1: _("Text document"), 2: _("Archive"), 3: _("Gif"), 4: _("Image"), 5: _("Audio"), 6: _("Video"), 7: _("Ebook"), 8: _("Unknown document")}
	user = session.get_user(document["owner_id"])
	title = document["title"]
	size = convert_bytes(document["size"])
	date = arrow.get(document["date"]).humanize(locale=languageHandler.curLang[:2])
	doc_type = doc_types[document["type"]]
	return [user["user1_nom"], title, doc_type, size, date]

def render_notification(notification, session):
	notification.pop("hide_buttons")
	print(notification["icon_type"])
#	print(notification["header"])
	print(notification)
	date = arrow.get(notification["date"]).humanize(locale=languageHandler.curLang[:2])
	msg = notification["header"]
#	msg = notification["header"]
#	if notification["type"] == "follow":
#		if len(notification["feedback"]) == 1:
#			user = session.get_user(notification["feedback"][0])
#			msg = _("{user1_nom} subscribed to your account").format(**user)
#		else:
#			users = ["{first_name} {last_name},".format(first_name=user["first_name"], last_name=user["last_name"]) for user in notification["feedback"]]
#			msg = " ".join(users)
#	print(msg)
	return [msg, date]