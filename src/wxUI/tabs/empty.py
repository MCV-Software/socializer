# -*- coding: utf-8 -*-
import wx

class emptyTab(wx.Panel):
	def __init__(self, parent, name):
		super(emptyTab, self).__init__(parent=parent, name=name)
		self.name = name
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)