# -*- coding: utf-8 -*-
import logging
from wxUI.tabs import notification
from .wall import wallBuffer

log = logging.getLogger("controller.buffers")

class notificationBuffer(wallBuffer):

    def create_tab(self, parent):
        self.tab = notification.notificationTab(parent)
        self.connect_events()
        self.tab.name = self.name

    def onFocus(self, event, *args, **kwargs):
        event.Skip()
