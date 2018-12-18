# -*- coding: utf-8 -*-
import wx
import application

def no_data_entered():
	return wx.MessageDialog(None, _(u"You must provide Both user and password."), _(u"Information needed"), wx.ICON_ERROR).ShowModal()

def no_update_available():
	return wx.MessageDialog(None, _(u"Your {0} version is up to date").format(application.name,), _(u"Update"), style=wx.OK).ShowModal()

def remove_buffer():
	return wx.MessageDialog(None, _(u"Do you really want to dismiss  this buffer?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def no_user_exist():
	wx.MessageDialog(None, _(u"This user does not exist"), _(u"Error"), style=wx.ICON_ERROR).ShowModal()

def show_error_code(code):
	title = ""
	message = ""
	if code == 201:
		title = _(u"Restricted access")
		message = _(u"Access to user's audio is denied by the owner. Error code {0}").format(code,)
	return wx.MessageDialog(None, message, title, style=wx.ICON_ERROR).ShowModal()

def bad_authorisation():
	return wx.MessageDialog(None, _(u"authorisation failed. Your configuration will not be saved. Please close and open again the application for authorising your account. Make sure you have typed your credentials correctly."), _(u"Error"), style=wx.ICON_ERROR).ShowModal()

def no_audio_albums():
	return wx.MessageDialog(None, _(u"You do not have audio albums to add tis file."), _(u"Error"), style=wx.ICON_ERROR).ShowModal()

def no_video_albums():
	return wx.MessageDialog(None, _(u"You do not have video albums to add tis file."), _(u"Error"), style=wx.ICON_ERROR).ShowModal()

def delete_audio_album():
	return wx.MessageDialog(None, _(u"Do you really want to delete   this Album? this will be deleted from VK too."), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()
