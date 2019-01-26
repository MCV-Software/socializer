# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import widgetUtils
import wx

class searchAudioDialog(widgetUtils.BaseDialog):
	def __init__(self, value=""):
		super(searchAudioDialog, self).__init__(None, -1)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetTitle(_("audio Search"))
		label = wx.StaticText(panel, -1, _("&Search"))
		self.term = wx.TextCtrl(panel, -1, value)
		dc = wx.WindowDC(self.term)
		dc.SetFont(self.term.GetFont())
		self.term.SetSize(dc.GetTextExtent("0"*40))
		sizer.Add(label, 0, wx.ALL, 5)
		sizer.Add(self.term, 0, wx.ALL, 5)
		radioSizer = wx.StaticBoxSizer(parent=panel, orient=wx.HORIZONTAL, label=_("Search by"))
		self.title  = wx.RadioButton(radioSizer.GetStaticBox(), wx.NewId(), _("Title"), style=wx.RB_GROUP)
		self.artist = wx.RadioButton(radioSizer.GetStaticBox(), wx.NewId(), _("Artist"))
		radioSizer.Add(self.title, 0, wx.ALL, 5)
		radioSizer.Add(self.artist, 0, wx.ALL, 5)
		sizer.Add(radioSizer, 0, wx.ALL, 5)
		sortBox = wx.StaticBoxSizer(parent=panel, orient=wx.HORIZONTAL, label=_("Sort by"))
		self.sortorder  = wx.ComboBox(sortBox.GetStaticBox(), wx.NewId(), choices=[_("Date added"), _("Duration"), _("Popularity")], value=_("Popularity"), style=wx.CB_READONLY)
		sortBox.Add(self.sortorder, 0, wx.ALL, 5)
		sizer.Add(sortBox, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _("&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
		btnsizer = wx.BoxSizer()
		btnsizer.Add(ok, 0, wx.ALL, 5)
		btnsizer.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def get_state(self, control):
		if getattr(self, control).GetValue() == True:
			return 1
		else:
			return 0

	def get_sort_order(self):
		return self.sortorder.GetSelection()

class searchVideoDialog(widgetUtils.BaseDialog):
	def __init__(self, value=""):
		super(searchVideoDialog, self).__init__(None, -1)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetTitle(_("video Search"))
		label = wx.StaticText(panel, -1, _("&Search"))
		self.term = wx.TextCtrl(panel, -1, value)
		dc = wx.WindowDC(self.term)
		dc.SetFont(self.term.GetFont())
		self.term.SetSize(dc.GetTextExtent("0"*40))
		sizer.Add(label, 0, wx.ALL, 5)
		sizer.Add(self.term, 0, wx.ALL, 5)
		sort_order = wx.StaticText(panel, -1, _("&Sort order by: "))
		self.sortorder  = wx.ComboBox(panel, wx.NewId(), choices=[_("Date added"), _("Duration"), _("Popularity")], value=_("Popularity"), style=wx.CB_READONLY)
		rBox = wx.BoxSizer(wx.HORIZONTAL)
		rBox.Add(sort_order, 0, wx.ALL, 5)
		rBox.Add(self.sortorder, 0, wx.ALL, 5)
		sizer.Add(rBox, 0, wx.ALL, 5)
		self.hd = wx.CheckBox(panel, wx.NewId(), _("Search only for videos in &High definition"))
		self.hd.SetValue(False)
		sizer.Add(self.hd, 0, wx.ALL, 5)
		self.safe_search = wx.CheckBox(panel, wx.NewId(), _("S&afe search"))
		self.safe_search.SetValue(True)
		sizer.Add(self.safe_search, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _("&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
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