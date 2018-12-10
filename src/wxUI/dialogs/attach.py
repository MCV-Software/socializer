# -*- coding: utf-8 -*-
import wx
import widgetUtils

class attachDialog(widgetUtils.BaseDialog):
	def __init__(self, voice_messages=False):
		super(attachDialog, self).__init__(None,  title=_(u"Add an attachment"))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl1 = wx.StaticText(panel, wx.NewId(), _(u"Attachments"))
		self.attachments = widgetUtils.list(panel, _(u"Type"), _(u"Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl1, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		sizer.Add(box, 0, wx.ALL, 5)
		static = wx.StaticBox(panel, label=_(u"Add attachments"))
		self.photo = wx.Button(panel, wx.NewId(), _(u"&Photo"))
		self.audio = wx.Button(panel, wx.NewId(), _(u"Audio file"))
		if voice_messages:
			self.voice_message = wx.Button(panel, wx.NewId(), _(u"Voice message"))
		self.remove = wx.Button(panel, wx.NewId(), _(u"Remove attachment"))
		self.remove.Enable(False)
		btnsizer = wx.StaticBoxSizer(static, wx.HORIZONTAL)
		btnsizer.Add(self.photo, 0, wx.ALL, 5)
		btnsizer.Add(self.audio, 0, wx.ALL, 5)
		if voice_messages:
			btnsizer.Add(self.voice_message, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
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
		openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return None
		dsc = self.ask_description()
		return (openFileDialog.GetPath(), dsc)

	def ask_description(self):
		dlg = wx.TextEntryDialog(self, _(u"please provide a description"), _(u"Description"))
		dlg.ShowModal()
		result = dlg.GetValue()
		dlg.Destroy()
		return result
