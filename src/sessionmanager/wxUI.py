# -*- coding: utf-8 -*-
import wx
import widgetUtils

def new_account_dialog():
	return wx.MessageDialog(None, _(u"In order to continue, you need to configure your VK account before. Would you like to autorhise a new account now?"), _(u"Authorisation"), wx.YES_NO).ShowModal()

class newSessionDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(newSessionDialog, self).__init__(parent=None, id=wx.NewId(), title=_(u"Authorise VK"))
		panel = wx.Panel(self)
		lbl1 = wx.StaticText(panel, -1, _(u"Email address"))
		self.email = wx.TextCtrl(panel, -1)
		lbl2 = wx.StaticText(panel, -1, _(u"Password"))
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