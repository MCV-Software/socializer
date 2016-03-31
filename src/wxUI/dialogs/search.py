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
		self.auto_complete = wx.CheckBox(panel, wx.NewId(), _(u"Try to &correct for mistakes in the search term"))
		self.auto_complete.SetValue(True)
		sizer.Add(self.auto_complete, 0, wx.ALL, 5)
		self.lyrics = wx.CheckBox(panel, wx.NewId(), _(u"Search only songs with associated &lyrics"))
		sizer.Add(self.lyrics, 0, wx.ALL, 5)
		self.artist_only  = wx.RadioButton(panel, wx.NewId(), _(u"Search all songs with this title"), style=wx.RB_GROUP)
		self.audios = wx.RadioButton(panel, wx.NewId(), _(u"Search audios of this artist"))
		radioSizer = wx.BoxSizer(wx.HORIZONTAL)
		radioSizer.Add(self.artist_only, 0, wx.ALL, 5)
		radioSizer.Add(self.audios, 0, wx.ALL, 5)
		sizer.Add(radioSizer, 0, wx.ALL, 5)
		sort_order = wx.StaticText(panel, -1, _(U"&Sort order by: "))
		self.sortorder  = wx.ComboBox(panel, wx.NewId(), choices=[_(u"Date added"), _(u"Duration"), _(u"Popularity")], value=_(u"Popularity"), style=wx.CB_READONLY)
		rBox = wx.BoxSizer(wx.HORIZONTAL)
		rBox.Add(sort_order, 0, wx.ALL, 5)
		rBox.Add(self.sortorder, 0, wx.ALL, 5)
		sizer.Add(rBox, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
		btnsizer = wx.BoxSizer()
		btnsizer.Add(ok, 0, wx.ALL, 5)
		btnsizer.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def get_checkable(self, control):
		if getattr(self, control).GetValue() == True:
			return 1
		else:
			return 0

	def get_sort_order(self):
		return self.sortorder.GetSelection()