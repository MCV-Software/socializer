# -*- coding: utf-8 -*-
""" A set of dialogs related to user and community profiles."""
from __future__ import unicode_literals
import wx
import widgetUtils

def text_size(wxObject, chars):
	""" Takes a wx object and the amount of characters supposed to hold and gives the best size for the control.
	wxObject wx.TextCtrl: Text control to be taken as a reference.
	chars int: Number of characters the control would hold.
	returns (x, y)"""
	dc = wx.WindowDC(wxObject)
	dc.SetFont(wxObject.GetFont())
	(x, y) = dc.GetMultiLineTextExtent("0"*chars)
	return (x, -1)

class mainInfo(wx.Panel):
	""" Panel to store main user information in a profile viewer."""

	def get(self, control):
		if hasattr(self, control):
			control = getattr(self, control)
			if hasattr(control, "GetValue"): return getattr(control, "GetValue")()
			elif hasattr(control, "GetLabel"): return getattr(control, "GetLabel")()
			else: return -1
		else: return 0

	def set(self, control, text):
		if hasattr(self, control):
			control = getattr(self, control)
			if hasattr(control, "SetValue"): return getattr(control, "SetValue")(text)
			elif hasattr(control, "SetLabel"): return getattr(control, "SetLabel")(text)
			elif hasattr(control, "ChangeValue"): return getattr(control, "ChangeValue")(text)
			else: return -1
		else: return 0

	def enable(self, control):
		getattr(self, control).Enable(True)

	def disable(self, control):
		getattr(self, control).Enable(False)

	def __init__(self, panel):
		super(mainInfo, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lblName = wx.StaticText(self, wx.NewId(), _("Name"))
		self.name = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.name.SetMinSize(text_size(self.name, 60))
		sizerName = wx.BoxSizer(wx.HORIZONTAL)
		sizerName.Add(lblName, 0, wx.ALL, 5)
		sizerName.Add(self.name, 0, wx.ALL, 5)
		sizer.Add(sizerName, 0, wx.ALL, 5)

		lblStatus = wx.StaticText(self, wx.NewId(), _("Status"))
		self.status = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.status.Enable(False)
		self.status.SetMinSize(text_size(self.status, 300))
		sizerStatus = wx.BoxSizer(wx.HORIZONTAL)
		sizerStatus.Add(lblStatus, 0, wx.ALL, 5)
		sizerStatus.Add(self.status, 0, wx.ALL, 5)
		sizer.Add(sizerStatus, 0, wx.ALL, 5)

		lblLastSeen = wx.StaticText(self, wx.NewId(), _("Last seen"))
		self.last_seen = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.last_seen.Enable(False)
		sizerLastSeen = wx.BoxSizer(wx.HORIZONTAL)
		sizerLastSeen.Add(lblLastSeen, 0, wx.ALL, 5)
		sizerLastSeen.Add(self.last_seen, 0, wx.ALL, 5)
		sizer.Add(sizerLastSeen, 0, wx.ALL, 5)

		lblBDate = wx.StaticText(self, wx.NewId(), _("Birthdate"))
		self.bdate = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.bdate.Enable(False)
		sizerBDate = wx.BoxSizer(wx.HORIZONTAL)
		sizerBDate.Add(lblBDate, 0, wx.ALL, 5)
		sizerBDate.Add(self.bdate, 0, wx.ALL, 5)
		sizer.Add(sizerBDate, 0, wx.ALL, 5)

		self.relation = wx.Button(self, -1, "")
		self.relation.Enable(False)
		sizer.Add(self.relation, 0, wx.ALL, 5)

		lblCity = wx.StaticText(self, wx.NewId(), _("Current city"))
		self.city = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.city.SetMinSize(text_size(self.city, 40))
		self.city.Enable(False)
		sizerCity = wx.BoxSizer(wx.HORIZONTAL)
		sizerCity.Add(lblCity, 0, wx.ALL, 5)
		sizerCity.Add(self.city, 0, wx.ALL, 5)
		sizer.Add(sizerCity, 0, wx.ALL, 5)

		lblHometown = wx.StaticText(self, wx.NewId(), _("Home Town"))
		self.home_town = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.home_town.SetMinSize(text_size(self.home_town, 40))
		self.home_town.Enable(False)
		sizerHometown = wx.BoxSizer(wx.HORIZONTAL)
		sizerHometown.Add(lblHometown, 0, wx.ALL, 5)
		sizerHometown.Add(self.home_town, 0, wx.ALL, 5)
		sizer.Add(sizerHometown, 0, wx.ALL, 5)

		lblWebsite = wx.StaticText(self, wx.NewId(), _("Website"))
		self.website = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)#size=(500, -1))
		self.website.SetMinSize(text_size(self.website, 90))
		self.website.Enable(False)
		self.go_site = wx.Button(self, -1, _("Visit website"))
		self.go_site.Enable(False)
		sizerWebsite = wx.BoxSizer(wx.HORIZONTAL)
		sizerWebsite.Add(lblWebsite, 0, wx.ALL, 5)
		sizerWebsite.Add(self.website, 1, wx.ALL, 5)
		sizerWebsite.Add(self.go_site, 1, wx.ALL, 5)
		sizer.Add(sizerWebsite, 1, wx.ALL, 5)

		lblOccupation = wx.StaticText(self, wx.NewId(), _("Occupation"))
		self.occupation = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.occupation.SetMinSize(text_size(self.occupation, 90))
		self.occupation.Enable(False)
		sizerOccupation = wx.BoxSizer(wx.HORIZONTAL)
		sizerOccupation.Add(lblOccupation, 0, wx.ALL, 5)
		sizerOccupation.Add(self.occupation, 0, wx.ALL, 5)
		sizer.Add(sizerOccupation, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class userProfile(widgetUtils.BaseDialog):
	def __init__(self, *args, **kwargs):
		super(userProfile, self).__init__(parent=None, *args, **kwargs)
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.notebook = wx.Notebook(self.panel)

	def create_controls(self, section):
		if section == "main_info":
			self.main_info = mainInfo(self.notebook)
			self.notebook.AddPage(self.main_info, _("Basic information"))
			self.main_info.SetFocus()

	def realice(self):
		self.image = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap(200, 200), size=(200, 200))
		self.sizer.Add(self.image, 1, wx.ALL, 10)
		self.sizer.Add(self.notebook, 1, wx.ALL, 5)
		cancel = wx.Button(self.panel, wx.ID_CANCEL)
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(cancel, 0, wx.ALL, 5)
		self.sizer.Add(btnSizer, 0, wx.ALL, 5)
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def get_value(self, panel, key):
		p = getattr(self, panel)
		return getattr(p, key).GetValue()

	def set_value(self, panel, key, value):
		p = getattr(self, panel)
		control = getattr(p, key)
		getattr(control, "SetValue")(value)

	def enable(self, panel, key, value=False):
		p = getattr(self, panel)
		control = getattr(p, key)
		getattr(control, "Enable")(value)