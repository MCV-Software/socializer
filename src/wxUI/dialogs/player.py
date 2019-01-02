# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class audioPlayerDialog(widgetUtils.BaseDialog):

	def __init__(self):
		super(audioPlayerDialog, self).__init__(None, wx.NewId(), _("Audio player"))
		sizer = wx.BoxSizer(wx.VERTICAL)