# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class blacklistDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(blacklistDialog, self).__init__(parent=None, title=_("blacklist"))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		box1 = wx.StaticBoxSizer(parent=panel, orient=wx.HORIZONTAL, label=_("blocked users"))
		self.persons = widgetUtils.list(panel, _("User"), style=wx.LC_REPORT)
		box1.Add(self.persons.list, 0, wx.ALL, 5)
		sizer.Add(box1, 0, wx.ALL, 5)
		self.unblock = wx.Button(panel, wx.NewId(), _("Unblock"))
		sizer.Add(self.unblock, 0, wx.ALL, 5)
		close = wx.Button(panel, wx.ID_CLOSE)
		sizer.Add(close, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())
