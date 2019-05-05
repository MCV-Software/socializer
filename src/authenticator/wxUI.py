# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import wx
import widgetUtils

def two_factor_auth():
	code = None
	dlg = wx.TextEntryDialog(None, _("Please provide the authentication code you have received from VK."), _("Two factor authentication code"))
	response = dlg.ShowModal()
	if response == widgetUtils.OK:
		code = dlg.GetValue()
	dlg.Destroy()
	return (code, True)

def bad_password():
	return wx.MessageDialog(None, _("Your password or email address are incorrect. Please fix the mistakes and try it again."), _("Wrong data"), wx.ICON_ERROR).ShowModal()