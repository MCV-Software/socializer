# -*- coding: utf-8 -*-
import logging
import wx
import widgetUtils
from .people import peopleBuffer

log = logging.getLogger("controller.buffers.communityPeople")

class communityPeopleBuffer(peopleBuffer):

    def get_menu(self, *args, **kwargs):
        user = self.get_post()
        m = wx.Menu()
        if user.get("can_post") == True:
            can_post = m.Append(wx.NewId(), _("&Post on user's wall"))
            widgetUtils.connect_event(m, widgetUtils.MENU, self.post, menuitem=can_post)
        if user.get("can_write_private_message") == True:
            can_write_message = m.Append(wx.Id(), _("Send message"))
            widgetUtils.connect_event(m, widgetUtils.MENU, self.new_chat, menuitem=can_write_message)
        profile = m.Append(wx.NewId(), _("View profile"))
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=profile)
        timeline = m.Append(wx.NewId(), _("Open timeline"))
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_timeline, menuitem=timeline)
        open_in_browser = m.Append(wx.NewId(), _("Open in vk.com"))
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_in_browser, menuitem=open_in_browser)
        return m
