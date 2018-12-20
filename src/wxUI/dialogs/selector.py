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
		self.indexes = []
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
			self.indexes.append(self.cb.GetSelection())

	def remove_user(self, *args, **kwargs):
		n = self.users.GetSelection()
		self.users.Delete(n)
		self.indexes.remove(n)

	def get_all_users(self):
		return self.indexes

class selectAttachment(widgetUtils.BaseDialog):

	def __init__(self, title="", attachments=[]):
		super(selectAttachment, self).__init__(parent=None, title=title)
		self.indexes = []
		self.attachments_list = attachments
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel, -1, _(u"Available attachments"))
		self.cb = wx.ComboBox(panel, -1, choices=attachments, value=attachments[0])
		self.cb.SetFocus()
		attachmentSizer = wx.BoxSizer()
		attachmentSizer.Add(label, 0, wx.ALL, 5)
		attachmentSizer.Add(self.cb, 0, wx.ALL, 5)
		self.add = wx.Button(panel, wx.NewId(), _(u"Select"))
		self.add.Bind(wx.EVT_BUTTON, self.add_attachment)
		attachmentSizer.Add(self.add, 0, wx.ALL, 5)
		sizer.Add(attachmentSizer, 0, wx.ALL, 5)
		lbl = wx.StaticText(panel, wx.NewId(), _(u"Selected attachments"))
		self.attachments = wx.ListBox(panel, -1)
		self.remove = wx.Button(panel, wx.NewId(), _(u"Remove"))
		self.remove.Bind(wx.EVT_BUTTON, self.remove_attachment)
		selectionSizer = wx.BoxSizer(wx.HORIZONTAL)
		selectionSizer.Add(lbl, 0, wx.ALL, 5)
		selectionSizer.Add(self.attachments, 0, wx.ALL, 5)
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

	def get_attachment(self):
		return self.cb.GetValue()

	def add_attachment(self, *args, **kwargs):
		selection = self.get_attachment()
		if selection in self.attachments_list:
			self.attachments.Append(selection)
			self.indexes.append(self.cb.GetSelection())
			self.remove.Enable(True)

	def remove_attachment(self, *args, **kwargs):
		n = self.attachments.GetSelection()
		self.attachments.Delete(n)
		self.indexes.pop(n)
		if len(self.indexes) == 0:
			self.remove.Enable(False)

	def get_all_attachments(self):
		return self.indexes