import os
from vk_api import VkApi

def get_vk():
	login = os.environ['LOGIN']
	password = os.environ['PASSWORD']
	vk = VkApi(login, password)
	vk.auth(token_only=True)
	return vk