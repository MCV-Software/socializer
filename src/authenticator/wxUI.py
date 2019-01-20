# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import wx
import widgetUtils

code = None
remember = True

def two_factor_auth():
	global code, remember
	wx.CallAfter(get_code)
	while code == None:
		time.sleep(0.5)
	return (code, remember)

def get_code():
	global code, remember
	dlg = wx.TextEntryDialog(None, _("Please provide the authentication code you have received from VK."), _("Two factor authentication code"))
	response = dlg.ShowModal()
	if response == widgetUtils.OK:
		code = dlg.GetValue()
		dlg.Destroy()
	dlg.Destroy()
