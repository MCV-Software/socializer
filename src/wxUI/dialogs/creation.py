# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class audio_album(widgetUtils.BaseDialog):

    def __init__(self, *args, **kwargs):
        super(audio_album, self).__init__(title=_("Create a new album"), parent=None)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(panel, wx.NewId(), _("Album title"))
        self.title = wx.TextCtrl(panel, wx.NewId())
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(lbl, 1, wx.ALL, 5)
        box.Add(self.title, 1, wx.ALL, 5)
        sizer.Add(box, 1, wx.ALL, 5)
        ok = wx.Button(panel, wx.ID_OK, _("&OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok, 0, wx.ALL, 5)
        btnsizer.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())
