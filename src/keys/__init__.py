# -*- coding: utf-8 -*-

keyring = None

def setup():
	global keyring
	if keyring == None:
		keyring = Keyring()

class Keyring(object):

	def get_api_key(self):
		return "5093442"