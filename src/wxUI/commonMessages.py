# -*- coding: utf-8 -*-
import wx
import application

def no_data_entered():
	return wx.MessageDialog(None, _(u"You must provide Both user and password."), _(u"Information needed"), wx.ICON_ERROR).ShowModal()

def no_update_available():
	return wx.MessageDialog(None, _(u"Your {0} version is up to date").format(application.name,), _(u"Update"), style=wx.OK).ShowModal()