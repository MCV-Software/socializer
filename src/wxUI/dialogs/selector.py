# -*- coding: utf-8 -*-
import wx
import widgetUtils

class selectAlbum(wx.Dialog):
 def __init__(self, title, albums):
  super(selectAlbum, self).__init__(parent=None, title=title)
  panel = wx.Panel(self)
  self.lista = wx.ListBox(panel, -1, choices=albums)
  self.lista.SetFocus()
  self.lista.SetSelection(0)
  self.lista.SetSize(self.lista.GetBestSize())
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(self.lista, 0, wx.ALL, 5)
  goBtn = wx.Button(panel, wx.ID_OK)
  goBtn.SetDefault()
  cancelBtn = wx.Button(panel, wx.ID_CANCEL)
  btnSizer = wx.BoxSizer()
  btnSizer.Add(goBtn, 0, wx.ALL, 5)
  btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_string(self):
  return self.lista.GetStringSelection()

 def get_item(self):
  return self.lista.GetSelection()

 def get_response(self):
  return self.ShowModal()

class selectPeople(widgetUtils.BaseDialog):

	def __init__(self, users=[]):
		super(selectPeople, self).__init__(parent=None, title=_(u"Tag friends"))
		self.users_list = users
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		userLabel = wx.StaticText(panel, -1, _(u"All friends"))
		self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0])
		self.cb.SetFocus()
		userSizer = wx.BoxSizer()
		userSizer.Add(userLabel, 0, wx.ALL, 5)
		userSizer.Add(self.cb, 0, wx.ALL, 5)
		self.add = wx.Button(panel, wx.NewId(), _(u"Select"))
		self.add.Bind(wx.EVT_BUTTON, self.add_user)
		userSizer.Add(self.add, 0, wx.ALL, 5)
		sizer.Add(userSizer, 0, wx.ALL, 5)
		lbl = wx.StaticText(panel, wx.NewId(), _(u"Tagged users"))
		self.users = wx.ListBox(panel, -1)
		self.remove = wx.Button(panel, wx.NewId(), _(u"Remove"))
		self.remove.Bind(wx.EVT_BUTTON, self.remove_user)
		selectionSizer = wx.BoxSizer(wx.HORIZONTAL)
		selectionSizer.Add(lbl, 0, wx.ALL, 5)
		selectionSizer.Add(self.users, 0, wx.ALL, 5)
		selectionSizer.Add(self.remove, 0, wx.ALL, 5)
		sizer.Add(selectionSizer, 0, wx.ALL, 5)
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

	def add_user(self, *args, **kwargs):
		selection = self.get_user()
		if selection in self.users_list:
			self.users.Append(selection)

	def remove_user(self, *args, **kwargs):
		self.users.Delete(self.users.GetSelection())

	def get_all_users(self):
		users = []
		for i in xrange(0, self.users.GetCount()):
			self.users.Select(i)
			users.append(self.users.GetStringSelection())
		return users