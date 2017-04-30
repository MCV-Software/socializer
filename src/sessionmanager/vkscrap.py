#!/usr/bin/python
import requests
from bs4 import BeautifulSoup as bs

class client(object):
	""" uses the movile version of the VK website for retrieving some information that is not available in the API, such as audio items."""
	def __init__(self, email, password):
		super(client, self).__init__()
		self.session = requests.session()
		self.email = email
		self.password = password

	def login(self):
		self.headers={"Referer": "https://m.vk.com/login?role=fast&to=&s=1&m=1&email=%s" % (self.email,),
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0'}
		payload = {"email": self.email, "pass": self.password}
		page = self.session.get("https://m.vk.com/login")
		soup = bs(page.content, "lxml")
		url = soup.find('form')['action']
		p = self.session.post(url, data=payload, headers=self.headers)

	def get_audios(self, user=None):
		if user == None:
			url = "https://m.vk.com/audio"
		else:
			url = "https://m.vk.com/audios{0}".format(user,)
		content = self.session.get(url)
		soup = bs(content.content, "lxml")
		divs = soup.find_all("div", class_="ai_info")
		return divs

	def parse_audio_info(self, info):
		artist = info("span", class_="ai_artist")[0].text
		year = info("span", class_="divider")[0].text
		title = info("span", class_="ai_title")[0].text
		duration = info("div", class_="ai_dur")[0].text
		return artist, title, year, duration

	def get_audio_url(self, url):
		if url == "" or url == None:
			return ""
		values = url.split("?extra=")[1].split("#")