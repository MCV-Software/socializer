# -*- coding: utf-8 -*-
import wx
import widgetUtils

class audioRecorderDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(audioRecorderDialog, self).__init__(None,  title=_(u"Record voice message"))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.play = wx.Button(panel, -1, _(u"&Play"))
		self.play.Disable()
		self.pause = wx.Button(panel, -1, _(u"&Pause"))
		self.pause.Disable()
		self.record = wx.Button(panel, -1, _(u"&Record"))
		self.record.SetFocus()
		self.discard = wx.Button(panel, -1, _(u"&Discard"))
		self.discard.Disable()
		ok = wx.Button(panel, wx.ID_OK, _(u"&Add"))
		cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Cancel"))
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.play, 0, wx.ALL, 5)
		btnSizer.Add(self.pause, 0, wx.ALL, 5)
		btnSizer.Add(self.record, 0, wx.ALL, 5)
		btnSizer2.Add(ok, 0, wx.ALL, 5)
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