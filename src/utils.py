# -*- coding: utf-8 -*-
""" Some utilities. I no have idea how I should put these, so..."""
import os
import requests
import re
import logging
from sessionmanager import session
log = logging.getLogger("utils")
url_re = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
bad_chars = '\'\\.,[](){}:;"'

def seconds_to_string(seconds, precision=0):
	day = seconds // 86400
	hour = seconds // 3600
	min = (seconds // 60) % 60
	sec = seconds - (hour * 3600) - (min * 60)
	sec_spec = "." + str(precision) + "f"
	sec_string = sec.__format__(sec_spec)
	string = ""
	if day == 1:
		string += _(u"%d day, ") % day
	elif day >= 2:
		string += _(u"%d days, ") % day
	if (hour == 1):
		string += _(u"%d hour, ") % hour
	elif (hour >= 2):
		string += _("%d hours, ") % hour
	if (min == 1):
		string += _(u"%d minute, ") % min
	elif (min >= 2):
		string += _(u"%d minutes, ") % min
	if sec >= 0 and sec <= 2:
		string += _(u"%s second") % sec_string
	else:
		string += _(u"%s seconds") % sec_string
	return string

def find_urls_in_text(text):
	return [s.strip(bad_chars) for s in url_re.findall(text)]

def download_file(url, local_filename, window):
	r = requests.get(url, stream=True)
	window.change_status(_(u"Downloading {0}").format(local_filename,))
	total_length = r.headers.get("content-length")
	dl = 0
	total_length = int(total_length)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=64): 
			if chunk: # filter out keep-alive new chunks
				dl += len(chunk)
				f.write(chunk)
				done = int(100 * dl / total_length)
				msg = _(u"Downloading {0} ({1}%)").format(os.path.basename(local_filename), done)
				window.change_status(msg)
	window.change_status(_(u"Ready"))
	return local_filename

def clean_text(text):
	""" Replaces all HTML entities and put the plain text equivalent if it's possible."""
	text = text.replace("<br>", "\n")
	text = text.replace("\\n", "\n")
	return text 

def add_attachment(attachment):
	msg = u""
	tpe = ""
	if attachment["type"] == "link":
		msg = u"{0}: {1}".format(attachment["link"]["title"], attachment["link"]["url"])
		tpe = _(u"Link")
	elif attachment["type"] == "photo":
		tpe = _(u"Photo")
		msg = attachment["photo"]["text"]
		if msg == "":
			msg = _(u"no description available")
	elif attachment["type"] == "video":
		msg = u"{0}".format(attachment["video"]["title"],)
		tpe = _(u"Video")
	elif attachment["type"] == "audio":
		msg = u"{0}".format(" ".join(session.compose_audio(attachment["audio"])))
		tpe = _(u"Audio")
	elif attachment["type"] == "doc":
		if attachment["doc"].has_key("preview") and attachment["doc"]["preview"].has_key("audio_msg"):
			tpe = _(u"Voice message")
			msg = seconds_to_string(attachment["doc"]["preview"]["audio_msg"]["duration"])
			print attachment["doc"]["ext"]
		else:
			msg = u"{0}".format(attachment["doc"]["title"])
			tpe = _(u"{0} file").format(attachment["doc"]["ext"])
	return [tpe, msg]

