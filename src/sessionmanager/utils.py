# -*- coding: utf-8 -*-
""" Some utilities. I no have idea how I should put these, so..."""
import os
import re
import html
import logging
import requests

log = logging.getLogger("utils")
url_re = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
bad_chars = '\'\\.,[](){}:;"'

def seconds_to_string(seconds, precision=0):
	""" convert a number of seconds in a string representation."""
	# ToDo: Improve it to handle properly Russian plurals.
	day = seconds // 86400
	hour = seconds // 3600
	min = (seconds // 60) % 60
	sec = seconds - (hour * 3600) - (min * 60)
	sec_spec = "." + str(precision) + "f"
	sec_string = sec.__format__(sec_spec)
	string = ""
	if day == 1:
		string += _("%d day, ") % day
	elif day >= 2:
		string += _("%d days, ") % day
	if (hour == 1):
		string += _("%d hour, ") % hour
	elif (hour >= 2):
		string += _("%d hours, ") % hour
	if (min == 1):
		string += _("%d minute, ") % min
	elif (min >= 2):
		string += _("%d minutes, ") % min
	if sec >= 0 and sec <= 2:
		string += _("%s second") % sec_string
	else:
		string += _("%s seconds") % sec_string
	return string

def find_urls_in_text(text):
	return [s.strip(bad_chars) for s in url_re.findall(text)]

def download_file(url, local_filename, window):
	r = requests.get(url, stream=True)
	window.change_status(_("Downloading {0}").format(local_filename,))
	total_length = r.headers.get("content-length")
	dl = 0
	total_length = int(total_length)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=64): 
			if chunk: # filter out keep-alive new chunks
				dl += len(chunk)
				f.write(chunk)
				done = int(100 * dl/total_length)
				msg = _("Downloading {0} ({1}%)").format(os.path.basename(local_filename), done)
				window.change_status(msg)
	window.change_status(_("Ready"))
	return local_filename

def download_files(downloads, window):
		for download in downloads:
			download_file(download[0], download[1], window)

def detect_users(text):
	""" Detect all users and communities mentionned in any text posted in VK."""
	# This regexp gets group and users mentionned in topic comments.
	for matched_data in re.finditer("(\[)(id|club)(\d+:bp-\d+_\d+\|)(\D+)(\])", text):
		text = re.sub("\[(id|club)\d+:bp-\d+_\d+\|\D+\]", matched_data.groups()[3]+", ", text, count=1)
	# This is for users and communities just mentionned in wall comments or posts.
	for matched_data in  re.finditer("(\[)(id|club)(\d+\|)(\D+)(\])", text):
		text = re.sub("\[(id|club)\d+\|\D+\]", matched_data.groups()[3]+", ", text, count=1)
	return text

def clean_text(text):
	""" Clean text, removing all unneeded HTMl and converting HTML represented characters in their unicode counterparts."""
	text = detect_users(text)
	text = html.unescape(text)
	return text

def transform_audio_url(url):
	""" Transforms the URL offered by VK to the unencrypted stream so we can still play it.
		This function will be updated every time VK decides to change something in their Audio API'S.
		Changelog:
		30/04/2019: Re-enabled old methods as VK changed everything as how it was working on 16.04.2019.
		17.04.2019: Updated function. Now it is not required to strip anything, just replacing /index.m3u8 with .mp3 should be enough.
		16.04.2019: Implemented this function. For now it replaces /index.m3u8 by .mp3, also removes the path component before "/audios" if the URL contains the word /audios, or the last path component before the filename if doesn't.
"""
	if "vkuseraudio.net" not in url and "index.m3u8" not in url:
		return url
	url = url.replace("/index.m3u8", ".mp3")
	parts = url.split("/")
	if "/audios" not in url:
		url = url.replace("/"+parts[-2], "")
	else:
		url = url.replace("/"+parts[-3], "")
	return url

def safe_filename(filename):
	allowed_symbols = ["_", ".", ",", "-", "(", ")"]
	return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ' or c in allowed_symbols]).rstrip()