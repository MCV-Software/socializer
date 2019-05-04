# -*- coding: utf-8 -*-
""" Set of methods used to retrieve access tokens by simulating the official VK application for Android. """
import random
import requests
import logging
from hashlib import md5
from .wxUI import two_factor_auth, bad_password

log = logging.getLogger("authenticator.official")

class AuthenticationError(Exception):
    pass

# Data extracted from official VK android APP.
client_id = "2274003"
client_secret = "hHbZxrka2uZ6jB1inYsH"
api_ver="5.93"
scope = "nohttps,all"
user_agent = "VKAndroidApp/5.23-2978 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en; 320x240)"

api_url = "https://api.vk.com/method/"

def get_device_id():
	""" Generate a random device ID, consisting in 16 alphanumeric characters."""
	return "".join(random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "a", "b", "c", "d", "e", "f"]) for _ in range(16))

def get_sig(method, values, secret):
	""" Create a signature for parameters passed to VK API. """
	postdata = ""
	for key in values:
		# None values should be excluded from SIG, otherwise VK won't validate it correctly.
		if values[key] != None:
			postdata = postdata + "{key}={value}&".format(key=key, value=values[key])
	# Remove the last "&" character.
	postdata = postdata[:-1]
	sig = md5(b"/method/"+method.encode("utf-8")+b"?"+postdata.encode("utf-8")+secret.encode("utf-8"))
	return sig.hexdigest()

def perform_request(method, postdata, secret):
	""" Send a request to VK servers by signing the data with the 'sig' parameter."""
	url = api_url+method
	sig = get_sig(method, postdata, secret)
	postdata.update(sig=sig)
	headers = {'User-Agent': user_agent}
	r = requests.post(url, data=postdata, headers=headers)
	return r.json()

def get_non_refreshed(login, password, scope=scope):
	""" Retrieves a non-refreshed token, this should be the first token needed to authenticate in VK.
	returns the access_token which still needs to be refreshed, device_id, and secret code, needed to sign all petitions in VK."""
	if not (login or password):
		raise ValueError("Both user and password are required.")
	device_id = get_device_id()
	# Let's authenticate.
	url = "https://oauth.vk.com/token"
	params = dict(grant_type="password",
		client_id=client_id, client_secret=client_secret, username=login,
		password=password, v=api_ver, scope=scope, lang="en", device_id=device_id)
	# Add two factor auth later due to python's syntax.
	params["2fa_supported"] = 1
	headers = {'User-Agent': user_agent}
	r = requests.get(url, params=params, headers=headers)
	log.exception(r.json())
	# If a 401 error is raised, we need to use 2FA here.
	# see https://vk.com/dev/auth_direct (switch lang to russian, english docs are very incomplete in the matter)
	# ToDo: this needs testing after implemented official VK tokens.
	if r.status_code == 401 and "phone_mask" in r.text:
		t = r.json()
		code, remember = two_factor_auth()
		url = "https://oauth.vk.com/token"
		params = dict(grant_type="password", lang="en",
			client_id=client_id, client_secret=client_secret, username=login,
			password=password, v=api_ver, scope=scope, device_id=device_id, code=code)
		r = requests.get(url, params=params, headers=headers)
		log.exception(r.json())
	if r.status_code == 200 and 'access_token' in r.text:
		log.exception(r.json())
		res = r.json()
		# Retrieve access_token and secret.
		access_token = res['access_token']
		secret = res['secret']
		return access_token, secret, device_id
	else:
		raise AuthenticationError(r.text)

def refresh_token(token, secret, device_id):
	method = "execute.getUserInfo"
	postdata = dict(v=api_ver, https=1, androidVersion=19, androidModel="Android SDK built for x86", info_fields="audio_ads,audio_background_limit,country,discover_design_version,discover_preload,discover_preload_not_seen,gif_autoplay,https_required,inline_comments,intro,lang,menu_intro,money_clubs_p2p,money_p2p,money_p2p_params,music_intro,audio_restrictions,profiler_settings,raise_to_record_enabled,stories,masks,subscriptions,support_url,video_autoplay,video_player,vklive_app,community_comments,webview_authorization,story_replies,animated_stickers,community_stories,live_section,playlists_download,calls,security_issue,eu_user,wallet,vkui_community_create,vkui_profile_edit,vkui_community_manage,vk_apps,stories_photo_duration,stories_reposts,live_streaming,live_masks,camera_pingpong,role,video_discover", device_id=device_id, lang="en", func_v=11, androidManufacturer="unknown", fields="photo_100,photo_50,exports,country,sex,status,bdate,first_name_gen,last_name_gen,verified,trending", access_token=token)
	perform_request(method, postdata, secret)
	method = "auth.refreshToken"
	postdata = dict(v=api_ver, https=1, timestamp=0, receipt2="", device_id=device_id, receipt="", lang="en", nonce="", access_token=token)
	return perform_request(method, postdata, secret)

def login(user, password):
	try:
		access_token, secret, device_id = get_non_refreshed(user, password)
		response = refresh_token(access_token, secret, device_id)
	except AuthenticationError:
		bad_password()
		raise AuthenticationError("")
	try:
		return response["response"]["token"], secret, device_id
	except KeyError:
		log.exception("An exception has occurred while attempting to authenticate. Printing response returned by vk...")
		log.exception(response)