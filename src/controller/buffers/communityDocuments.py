# -*- coding: utf-8 -*-
import logging
from wxUI.tabs import home
from .documents import documentsBuffer

log = logging.getLogger("controller.buffers.communityDocuments")

class communityDocumentsBuffer(documentsBuffer):
	can_get_items = True

	def create_tab(self, parent):
		self.tab = home.documentCommunityTab(parent)
		self.connect_events()
		self.tab.name = self.name
		if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
			self.tab.post.Enable(False)