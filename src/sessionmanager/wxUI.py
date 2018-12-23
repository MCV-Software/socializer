# -*- coding: utf-8 -*-
import time
import wx
import widgetUtils

code = None
remember = True

def new_account_dialog():
	return wx.MessageDialog(None, _(u"In order to continue, you need to configure your VK account before. Would you like to autorhise a new account now?"), _(u"Authorisation"), wx.YES_NO).ShowModal()

def two_factor_auth():
	global code, remember
	wx.CallAfter(get_code)
	while code == None:
		time.sleep(0.5)
	return (code, remember)

def get_code():
	global code, remember
	dlg = wx.TextEntryDialog(None, _(u"Please provide the authentication code you have received from VK."), _(u"Two factor authentication code"))
	response = dlg.ShowModal()
	if response == widgetUtils.OK:
		code = dlg.GetValue()
		dlg.Destroy()

	dlg.Destroy()

def two_factor_question():
	return wx.MessageDialog(None, _(u"Do you have two factor authentication enabled in your account?"), _(u"Authentication method"), wx.YES_NO).ShowModal()

class newSessionDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(newSessionDialog, self).__init__(parent=None, id=wx.NewId(), title=_(u"Authorise VK"))
		panel = wx.Panel(self)
		lbl1 = wx.StaticText(panel, -1, _(u"&Email or phone number"))
		self.email = wx.TextCtrl(panel, -1)
		lbl2 = wx.StaticText(panel, -1, _(u"&Password"))
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