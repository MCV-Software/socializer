# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class attachDialog(widgetUtils.BaseDialog):
	def __init__(self, voice_messages=False):
		super(attachDialog, self).__init__(None,  title=_("Add an attachment"))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl1 = wx.StaticText(panel, wx.NewId(), _("Attachments"))
		self.attachments = widgetUtils.list(panel, _("Type"), _("Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl1, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		sizer.Add(box, 0, wx.ALL, 5)
		static = wx.StaticBoxSizer(parent=panel, orient=wx.HORIZONTAL, label=_("Add attachments"))
		self.photo = wx.Button(static.GetStaticBox(), wx.NewId(), _("&Photo"))
		self.audio = wx.Button(static.GetStaticBox(), wx.NewId(), _("Audio file"))
		self.document = wx.Button(static.GetStaticBox(), wx.NewId(), _("Document"))
		if voice_messages:
			self.voice_message = wx.Button(static.GetStaticBox(), wx.NewId(), _("Voice message"))
		self.remove = wx.Button(static.GetStaticBox(), wx.NewId(), _("Remove attachment"))
		self.remove.Enable(False)
		static.Add(self.photo, 0, wx.ALL, 5)
		static.Add(self.audio, 0, wx.ALL, 5)
		static.Add(self.document, 0, wx.ALL, 5)
		if voice_messages:
			static.Add(self.voice_message, 0, wx.ALL, 5)
		sizer.Add(static, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK)
		ok.SetDefault()
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		btnSizer = wx.BoxSizer()
		btnSizer.Add(ok, 0, wx.ALL, 5)
		btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
		sizer.Add(btnSizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def get_image(self):
		openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return None
		dsc = self.ask_description()
		return (openFileDialog.GetPath(), dsc)

	def ask_description(self):
		dlg = wx.TextEntryDialog(self, _("please provide a description"), _("Description"))
		dlg.ShowModal()
		result = dlg.GetValue()
		dlg.Destroy()
		return result

	def get_audio(self):
		openFileDialog = wx.FileDialog(self, _("Select the audio file to be uploaded"), "", "", _("Audio files (*.mp3)|*.mp3"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return None
		return openFileDialog.GetPath()

	def get_document(self):
		openFileDialog = wx.FileDialog(self, _("Select the file to be uploaded. All extensions are allowed except .mp3 and .exe."), "", "", _("All files (*.*)|*.*"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return None
		return openFileDialog.GetPath()

	def invalid_attachment(self):
		return wx.MessageDialog(None, _("The file you are trying to upload contains an extension that is not allowed by VK."), _("Error"), style=wx.ICON_ERROR).ShowModal()