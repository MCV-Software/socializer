# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class timelineDialog(widgetUtils.BaseDialog):

	def __init__(self, users=[]):
		super(timelineDialog, self).__init__(parent=None, title=_("New timeline for {0}").format(users[0],))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		userLabel = wx.StaticText(panel, -1, _("User"))
		self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0])
		self.cb.SetFocus()
		userSizer = wx.BoxSizer()
		userSizer.Add(userLabel, 0, wx.ALL, 5)
		userSizer.Add(self.cb, 0, wx.ALL, 5)
		actionsSizer = wx.StaticBoxSizer(parent=panel, orient=wx.VERTICAL, label=_("Buffer type"))
		self.wall    = wx.RadioButton(actionsSizer.GetStaticBox(), wx.NewId(), _("&Wall posts"), style=wx.RB_GROUP)
		self.audio = wx.RadioButton(actionsSizer.GetStaticBox(), wx.NewId(), _("Audio"))
		self.friends = wx.RadioButton(actionsSizer.GetStaticBox(), wx.NewId(), _("Friends"))
		actionsSizer.Add(self.wall, 0, wx.ALL, 5)
		actionsSizer.Add(self.audio, 0, wx.ALL, 5)
		actionsSizer.Add(self.friends, 0, wx.ALL, 5)
		sizer.Add(actionsSizer, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _("&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		btnsizer.Add(ok, 0, wx.ALL, 5)
		btnsizer.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def get_user(self):
		return self.cb.GetValue()

	def get_buffer_type(self):
		if self.audio.GetValue() == True:
			return "audio"
		elif self.wall.GetValue() == True:
			return "wall"
		elif self.friends.GetValue() == True:
			return "friends"