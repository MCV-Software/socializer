# -*- coding: utf-8 -*-
""" A chat GUI to be used in socializer. """
import wx
import widgetUtils
from pubsub import pub

class chatTab(wx.Panel):

	def insert_attachments(self, attachments):
		""" Insert a list of previously rendered attachments in the tab's attachments list.
		@ attachments list: A list of attachments already rendered.
		"""
		for i in attachments:
			self.attachments.insert_item(False, *i)

	def __init__(self, parent):
		super(chatTab, self).__init__(parent=parent)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.create_controls())
		sizer.Add(self.create_attachments(), 0, wx.ALL, 5)
		sizer.Add(self.create_chat(), 0, wx.ALL, 5)
		self.attachment = wx.Button(self, wx.NewId(), _("Add"))
		self.actions = wx.Button(self, wx.NewId(), _("Actions"))
		buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
		buttonsBox.Add(self.attachment, 0, wx.ALL, 5)
		buttonsBox.Add(self.actions, 0, wx.ALL, 5)
		sizer.Add(buttonsBox, 0, wx.ALL, 5)
		self.send = wx.Button(self, -1, _("Send"))
		sizer.Add(self.send, 0, wx.ALL, 5)
		self.SetSizer(sizer)

	def create_controls(self):
		lbl1 = wx.StaticText(self, wx.NewId(), _("History"))
		self.history = wx.TextCtrl(self, wx.NewId(), style=wx.TE_READONLY|wx.TE_MULTILINE, size=(500, 300))
		selectId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
		self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('A'), selectId)])
		self.SetAcceleratorTable(self.accel_tbl)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl1, 0, wx.ALL, 5)
		box.Add(self.history, 0, wx.ALL, 5)
		return box

	def onSelect(self, event, *args, **kwargs):
		if self.history.HasFocus():
			self.history.SelectAll()
		else:
			self.text.SelectAll()
		event.Skip()

	def create_attachments(self):
		lbl = wx.StaticText(self, -1, _("Attachments"))
		self.attachments = widgetUtils.list(self, _("Type"), _("Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		return box

	def create_chat(self):
		lbl2 = wx.StaticText(self, -1, _("Write a message"))
		self.text = wx.TextCtrl(self, -1, size=(400, -1), style=wx.TE_MULTILINE)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl2, 0, wx.ALL, 20)
		box.Add(self.text, 0, wx.ALL, 5)
		return box

	def set_focus_function(self, focus_function):
		self.history.Bind(wx.EVT_KEY_UP , focus_function)

	def add_message(self, message, reverse=False):
		old_line = self.history.GetNumberOfLines()#.count("\n")
		point = self.history.GetInsertionPoint()
		if reverse:
			wx.CallAfter(self.history.SetValue, message+"\n"+self.history.GetValue())
		else:
			wx.CallAfter(self.history.AppendText, message+"\n")
		wx.CallAfter(self.history.SetInsertionPoint, point)
		new_line = self.history.GetNumberOfLines()#.count("\n")
		return (old_line, new_line)