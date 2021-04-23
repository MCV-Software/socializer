# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
import logging
import output
from wxUI.tabs import home

log = logging.getLogger("controller.buffers.empty")

class emptyBuffer(object):

	def __init__(self, name=None, parent=None, *args, **kwargs):
		self.tab = home.empty(parent=parent, name=name)
		self.name = name

	def get_items(self, *args, **kwargs):
		if not hasattr(self, "tab"):
			# Create GUI associated to this buffer.
			self.create_tab(self.parent)
			# Add name to the new control so we could look for it when needed.
			self.tab.name = self.name
		pass

	def get_more_items(self, *args, **kwargs):
		output.speak(_("This buffer doesn't support getting more items."))

	def remove_buffer(self, mandatory=False):
		return False