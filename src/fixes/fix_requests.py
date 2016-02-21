# -*- coding: utf-8 -*-
import requests
import paths
import os


def fix():
	os.environ["REQUESTS_CA_BUNDLE"] = paths.app_path("cacert.pem")