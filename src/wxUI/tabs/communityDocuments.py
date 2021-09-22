# -*- coding: utf-8 -*-
import wx
import widgetUtils
from .home import homeTab

class communityDocumentsTab(homeTab):
    def create_list(self):
        self.lbl = wx.StaticText(self, wx.NewId(), _("Documents"))
        self.list = widgetUtils.list(self, *[_("User"), _("Title"), _("Type"), _("Size"), _("Date")], style=wx.LC_REPORT)
        self.list.set_windows_size(0, 200)
        self.list.set_windows_size(1, 128)
        self.list.set_windows_size(2, 35)
        self.list.set_windows_size(3, 15)
        self.list.set_windows_size(4, 25)
        self.list.set_size()
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

    def get_download_path(self, filename):
        saveFileDialog = wx.FileDialog(self, _("Save document as"), "", filename, _("All files (*.*)|*.*"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == widgetUtils.OK:
            return saveFileDialog.GetPath()
