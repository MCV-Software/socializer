# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pubsub import pub
from interactors import configuration as interactor

class basePresenter(object):

	def __init__(self, view, interactor, modulename):
		self.interactor = interactor
		self.view = view
		self.interactor.install(view=view, presenter=self, modulename=modulename)

	def run(self):
		self.interactor.start()
		self.interactor.uninstall()