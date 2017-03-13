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
