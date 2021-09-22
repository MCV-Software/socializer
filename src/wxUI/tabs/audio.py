# -*- coding: utf-8 -*-
import wx
import widgetUtils
from .home import homeTab

class audioTab(homeTab):
    def create_list(self):
        self.lbl = wx.StaticText(self, wx.NewId(), _("Mu&sic"))
        self.list = widgetUtils.multiselectionList(self, *[_("Title"), _("Artist"), _("Duration")], style=wx.LC_REPORT, name=_("Music"))
        self.list.set_windows_size(0, 160)
        self.list.set_windows_size(1, 380)
        self.list.set_windows_size(2, 80)
        self.list.set_size()
        self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnKeyDown)

    def create_post_buttons(self):
        self.postBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Actions"))
        self.post = wx.Button(self.postBox.GetStaticBox(), -1, _("&Upload audio"))
        self.post.Enable(False)
        self.play = wx.Button(self.postBox.GetStaticBox(), -1, _("P&lay"))
        self.play_all = wx.Button(self.postBox.GetStaticBox(), -1, _("Play &All"))
        self.postBox.Add(self.post, 0, wx.ALL, 5)
        self.postBox.Add(self.play, 0, wx.ALL, 5)
        self.postBox.Add(self.play_all, 0, wx.ALL, 5)

    def get_file_to_upload(self):
        openFileDialog = wx.FileDialog(self, _("Select the audio file to be uploaded"), "", "", _("Audio files (*.mp3)|*.mp3"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return None
        return openFileDialog.GetPath()

    def get_download_path(self, filename="", multiple=False):
        if multiple == False:
            d = wx.FileDialog(self, _("Save this file"), "", filename, _("Audio Files(*.mp3)|*.mp3"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        else:
            d = wx.DirDialog(None, _("Select a folder to save all files"))
        if d.ShowModal() == wx.ID_OK:
            return d.GetPath()
        d.Destroy()
