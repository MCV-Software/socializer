# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class audioRecorderDialog(widgetUtils.BaseDialog):
    def __init__(self):
        super(audioRecorderDialog, self).__init__(None,  title=_("Record voice message"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.play = wx.Button(panel, -1, _("&Play"))
        self.play.Disable()
        self.record = wx.Button(panel, -1, _("&Record"))
        self.record.SetFocus()
        self.discard = wx.Button(panel, -1, _("&Discard"))
        self.discard.Disable()
        self.ok = wx.Button(panel, wx.ID_OK, _("&Add"))
        cancel = wx.Button(panel, wx.ID_CANCEL, _("&Cancel"))
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.play, 0, wx.ALL, 5)
        btnSizer.Add(self.record, 0, wx.ALL, 5)
        btnSizer2.Add(self.ok, 0, wx.ALL, 5)
        btnSizer2.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(btnSizer, 0, wx.ALL, 5)
        sizer.Add(btnSizer2, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())

    def enable_control(self, control):
        if hasattr(self, control):
            getattr(self, control).Enable()

    def disable_control(self, control):
        if hasattr(self, control):
            getattr(self, control).Disable()
