# -*- coding: utf-8 -*-
import wx
import widgetUtils

class audioPlayerDialog(widgetUtils.BaseDialog):

	def __init__(self):
		super(audioPlayerDialog, self).__init__(None, wx.NewId(), _(u"Audio player"))
		sizer = wx.BoxSizer(wx.VERTICAL)