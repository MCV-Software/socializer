# -*- coding: utf-8 -*-
import widgetUtils
import wx

class searchAudioDialog(widgetUtils.BaseDialog):
	def __init__(self, value=""):
		super(searchAudioDialog, self).__init__(None, -1)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetTitle(_(u"audio Search"))
		label = wx.StaticText(panel, -1, _(u"&Search"))
		self.term = wx.TextCtrl(panel, -1, value)
		dc = wx.WindowDC(self.term)
		dc.SetFont(self.term.GetFont())
		self.term.SetSize(dc.GetTextExtent("0"*40))
		sizer.Add(label, 0, wx.ALL, 5)
		sizer.Add(self.term, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
		btnsizer = wx.BoxSizer()
		btnsizer.Add(ok, 0, wx.ALL, 5)
		btnsizer.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())
