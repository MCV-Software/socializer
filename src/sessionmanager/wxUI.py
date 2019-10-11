# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

def new_account_dialog():
	return wx.MessageDialog(None, _("In order to continue, you need to configure your VK account before. Would you like to autorhise a new account now?"), _("Authorisation"), wx.YES_NO).ShowModal()

class newSessionDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(newSessionDialog, self).__init__(parent=None, id=wx.NewId(), title=_("Authorise VK"))
		panel = wx.Panel(self)
		lbl1 = wx.StaticText(panel, -1, _("&Email or phone number"))
		self.email = wx.TextCtrl(panel, -1)
		lbl2 = wx.StaticText(panel, -1, _("&Password"))
		self.passw = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD)
		sizer = wx.BoxSizer()
		b1 = wx.BoxSizer(wx.HORIZONTAL)
		b1.Add(lbl1, 0, wx.ALL, 5)
		b1.Add(self.email, 0, wx.ALL, 5)
		b2 = wx.BoxSizer(wx.HORIZONTAL)
		b2.Add(lbl2, 0, wx.ALL, 5)
		b2.Add(self.passw, 0, wx.ALL, 5)
		sizer.Add(b1, 0, wx.ALL, 5)
		sizer.Add(b2, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK)
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL)
		btnb = wx.BoxSizer(wx.HORIZONTAL)
		btnb.Add(ok, 0, wx.ALL, 5)
		btnb.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnb, 0, wx.ALL, 5)
		panel.SetSizer(sizer)

	def get_email(self):
		return self.email.GetValue()

	def get_password(self):
		return self.passw.GetValue()

class sessionManagerWindow(widgetUtils.BaseDialog):
	def __init__(self, title, starting=True):
		super(sessionManagerWindow, self).__init__(parent=None, title=title, size=wx.DefaultSize)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(panel, -1, _(u"Accounts list"), size=wx.DefaultSize)
		listSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.list = widgetUtils.list(panel, _("Account"), style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
		listSizer.Add(label, 0, wx.ALL, 5)
		listSizer.Add(self.list.list, 0, wx.ALL, 5)
		sizer.Add(listSizer, 0, wx.ALL, 5)
		self.new = wx.Button(panel, -1, _("New account"), size=wx.DefaultSize)
		self.remove = wx.Button(panel, -1, _(u"Remove account"))
		if starting:
			id_ok = wx.ID_OK
		else:
			id_ok = wx.ID_CANCEL
		ok = wx.Button(panel, id_ok, size=wx.DefaultSize)
		ok.SetDefault()
		if starting:
			cancel = wx.Button(panel, wx.ID_CANCEL, size=wx.DefaultSize)
		self.SetAffirmativeId(id_ok)
		buttons = wx.BoxSizer(wx.HORIZONTAL)
		buttons.Add(self.new, 0, wx.ALL, 5)
		buttons.Add(ok, 0, wx.ALL, 5)
		if starting:
			buttons.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(buttons, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		min = sizer.CalcMin()
		self.SetClientSize(min)

	def remove_account_dialog(self):
		return wx.MessageDialog(self, _("Do you really want to delete this account?"), _("Remove account"), wx.YES_NO).ShowModal()