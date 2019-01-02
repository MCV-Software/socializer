# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import application

def no_data_entered():
	return wx.MessageDialog(None, _("You must provide Both user and password."), _("Information needed"), wx.ICON_ERROR).ShowModal()

def no_update_available():
	return wx.MessageDialog(None, _("Your {0} version is up to date").format(application.name,), _("Update"), style=wx.OK).ShowModal()

def remove_buffer():
	return wx.MessageDialog(None, _("Do you really want to dismiss  this buffer?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def no_user_exist():
	wx.MessageDialog(None, _("This user does not exist"), _("Error"), style=wx.ICON_ERROR).ShowModal()

def show_error_code(code):
	title = ""
	message = ""
	if code == 201:
		title = _("Restricted access")
		message = _("Access to user's audio is denied by the owner. Error code {0}").format(code,)
	return wx.MessageDialog(None, message, title, style=wx.ICON_ERROR).ShowModal()

def bad_authorisation():
	return wx.MessageDialog(None, _("authorisation failed. Your configuration will not be saved. Please close and open again the application for authorising your account. Make sure you have typed your credentials correctly."), _("Error"), style=wx.ICON_ERROR).ShowModal()

def no_audio_albums():
	return wx.MessageDialog(None, _("You do not have audio albums to add tis file."), _("Error"), style=wx.ICON_ERROR).ShowModal()

def no_video_albums():
	return wx.MessageDialog(None, _("You do not have video albums to add tis file."), _("Error"), style=wx.ICON_ERROR).ShowModal()

def delete_audio_album():
	return wx.MessageDialog(None, _("Do you really want to delete   this Album? this will be deleted from VK too."), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def updated_status():
	return wx.MessageDialog(None, _("Your status message has been successfully updated."), _("Success")).ShowModal()