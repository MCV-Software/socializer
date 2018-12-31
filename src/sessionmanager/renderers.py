# -*- coding: utf-8 -*-
""" this module contains everything used to render different kind of posts (posts in the home buffer,
Chat messages, audios, videos, photos, comments in posts, etc)"""
import arrow
import languageHandler
import logging
import utils

log = logging.getLogger(__file__)

### Some util funtions

def extract_attachment(attachment):
	""" Adds information about attachment files in posts. It only adds the text, I mean, no attachment file is added here.
	This will produce a result like:
	'website: http://url.com'.
	'photo: A forest'."""
	msg = u""
	if attachment["type"] == "link":
		msg = u"{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
	elif attachment["type"] == "photo":
		msg = attachment["photo"]["text"]
		if msg == "":
			return _(u"photo with no description available")
	elif attachment["type"] == "video":
		msg = _(u"video: {0}").format(attachment["video"]["title"],)
	return msg

def short_text(status):
	""" This shorts the text to 140 characters for displaying it in the list control of buffers."""
	message = ""
	# copy_story indicates that the post is a shared repost.
	if status.has_key("copy_history"):
		txt = status["copy_history"][0]["text"]
	else:
		txt = status["text"]
	if len(txt) < 140:
		message = utils.clean_text(txt)
	else:
		message = utils.clean_text(txt[:139])
	return message

def clean_audio(audio):
	""" Remove unavailable songs due to different reasons. This is used to clean the audio list when people adds audios and need to be displayed in the buffer."""
	for i in audio["items"][:]:
		if type(i) == bool:
			audio["items"].remove(i)
			audio["count"] = audio["count"] -1
	return audio

### Render functions

def render_person(status, session):
	""" Render users in people buffers such as everything related to friendships or buffers created with only people.
	Example result: ["John Doe", "An hour ago"]
	Reference: https://vk.com/dev/fields"""
	if status.has_key("last_seen"):
		original_date = arrow.get(status["last_seen"]["time"])
		# Translators: This is the date of last seen
		last_seen = _(u"{0}").format(original_date.humanize(locale=languageHandler.curLang[:2]),)
	# Account suspended or deleted.
	elif status.has_key("last_seen") == False and status.has_key("deactivated"):
			last_seen = _(u"Account deactivated")
	return [u"{0} {1}".format(status["first_name"], status["last_name"]), last_seen]

def render_newsfeed_item(status, session):
	""" This me☻thod is used to render an item of the news feed.
	References:
		https://vk.com/dev/newsfeed.get
		https://vk.com/dev/post_source
		https://vk.com/dev/post
	"""
	user = session.get_user_name(status["source_id"], case_name="nom")
	# See if this is a post or repost.
	if status.has_key("copy_history"):
		user = _(u"{0} has shared the {1}'s post").format(user, session.get_user_name(status["copy_history"][0]["owner_id"]))
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.curLang[:2])
	# handle status updates.
	if status["type"] == "post":
		message += short_text(status)
		if status.has_key("attachment") and len(status["attachment"]) > 0:
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
			message = _(u"{0} has added  an audio: {1}").format(user, u", ".join(render_audio(status["audio"]["items"][0], session)),)
		else:
			prem = ""
			for i in xrange(0, status["audio"]["count"]):
				composed_audio = render_audio(status["audio"]["items"][i], session)
				prem += u"{0} - {1}, ".format(composed_audio[0], composed_audio[1])
			message = _(u"{0} has added  {1} audios: {2}").format(user, status["audio"]["count"], prem)
	# Handle audio playlists
	elif status["type"] == "audio_playlist":
		if status["audio_playlist"]["count"] == 1:
			message = _(u"{0} has added an audio album: {1}, {2}").format(user, status["audio_playlist"]["items"][0]["title"], status["audio_playlist"]["items"][0]["description"])
		else:
			prestring = ""
			for i in xrange(0, status["audio_playlist"]["count"]):
				prestring += u"{0} - {1}, ".format(status["audio_playlist"]["items"][i]["title"], status["audio_playlist"]["items"][i]["description"])
			message = _(u"{0} has added  {1} audio albums: {2}").format(user, status["audio_playlist"]["count"], prestring)

	# handle new friends for people in the news buffer.
	elif status["type"] == "friend":
		msg_users = u""
		if status.has_key("friends"):
			for i in status["friends"]["items"]:
				msg_users = msg_users + u"{0}, ".format(session.get_user_name(i["user_id"], "nom"))
		else:
			print status.keys()
		message = _(u"{0} added friends: {1}").format(user, msg_users)
	elif status["type"] == "video":
		if status["video"]["count"] == 1:
			message = _(u"{0} has added  a video: {1}").format(user, u", ".join(render_video(status["video"]["items"][0], session)),)
		else:
			prem = ""
			for i in xrange(0, status["video"]["count"]):
				composed_video = render_video(status["video"]["items"][i], session)
				prem += u"{0} - {1}, ".format(composed_video[0], composed_video[1])
			message = _(u"{0} has added  {1} videos: {2}").format(user, status["video"]["count"], prem)
	else:
		if status["type"] != "post": print status
	return [user, message, created_at]

def render_message(message, session):
	""" Render a message posted in a private conversation.
	Reference: https://vk.com/dev/message"""
	user = session.get_user_name(message["from_id"], "nom")
	original_date = arrow.get(message["date"])
	now = arrow.now()
	original_date = original_date.to(now.tzinfo)
	# Format the date here differently depending in if this is the same day for both dates or not.
	if original_date.day == now.day:
		created_at = original_date.format(_(u"H:mm."), locale=languageHandler.curLang[:2])
	else:
		created_at = original_date.format(_(u"H:mm. dddd, MMMM D, YYYY"), locale=languageHandler.curLang[:2])
	# No idea why some messages send "text" instead "body"
	if message.has_key("body"):
		body = message["body"]
	else:
		body = message["text"]
	return [u"{2}, {0} {1}".format(body, created_at, user)]

def render_status(status, session):
	""" Render a wall post (shown in user's wall, not in newsfeed).
	Reference: https://vk.com/dev/post"""
	user = session.get_user_name(status["from_id"], "nom")
	if status.has_key("copy_history"):
		user = _(u"{0} has shared the {1}'s post").format(user, session.get_user_name(status["copy_history"][0]["owner_id"]))
	message = ""
	original_date = arrow.get(status["date"])
	created_at = original_date.humanize(locale=languageHandler.curLang[:2])
	if status.has_key("copy_owner_id"):
		user = _(u"{0} has shared the {1}'s post").format(user, session.get_user_name(status["copy_owner_id"]))
	if status["post_type"] == "post" or status["post_type"] == "copy":
		message += short_text(status)
	if status.has_key("attachment") and len(status["attachment"]) > 0:
		message += extract_attachment(status["attachment"])
		if message == "":
			message = "no description available"
	return [user, message, created_at]

def render_audio(audio, session=None):
	""" Render audio files added to VK.
	Example result:
	["Song title", "Artist", "03:15"]
	reference: https://vk.com/dev/audio_object"""
	if audio == False: return [_(u"Audio removed from library"), "", ""]
	return [audio["title"], audio["artist"], utils.seconds_to_string(audio["duration"])]

def render_video(video, session=None):
	""" Render a video file from VK.
	Example result:
	["Video title", "Video description", "01:30:28"]
	Reference: https://vk.com/dev/video_object"""
	if video == False:
		return [_(u"Video not available"), "", ""]
	return [video["title"], video["description"], utils.seconds_to_string(video["duration"])]

def render_audio_message(audio_message, session=None):
	""" Render a voice message from VK
	Example result:
	["Voice message", "01:30:28"]"""
	if audio_message == False:
		return [_(u"Voice message not available"), "", ""]
	return [utils.seconds_to_string(audio_message["duration"])]