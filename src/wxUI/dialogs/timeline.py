# -*- coding: utf-8 -*-
import wx
import widgetUtils

class timelineDialog(widgetUtils.BaseDialog):

	def __init__(self, users=[]):
		super(timelineDialog, self).__init__(parent=None, title=_(u"New timeline for {0}").format(users[0],))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		userLabel = wx.StaticText(panel, -1, _(u"User"))
		self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0])
		self.cb.SetFocus()
		userSizer = wx.BoxSizer()
		userSizer.Add(userLabel, 0, wx.ALL, 5)
		userSizer.Add(self.cb, 0, wx.ALL, 5)
		actionsstatic = wx.StaticBox(panel, label=_(u"Buffer type"))
		self.audio   = wx.RadioButton(panel, wx.NewId(), _(u"&Audios"), style=wx.RB_GROUP)
		radioSizer = wx.StaticBoxSizer(actionsstatic, wx.HORIZONTAL)
		radioSizer.Add(self.audio, 0, wx.ALL, 5)
		sizer.Add(radioSizer, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
		btnsizer = wx.BoxSizer()
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