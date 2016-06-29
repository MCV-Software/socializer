# -*- coding: utf-8 -*-
import wx

class selectAlbum(wx.Dialog):
 def __init__(self, title, albums):
  super(selectAlbum, self).__init__(parent=None, title=title)
  panel = wx.Panel(self)
  self.lista = wx.ListBox(panel, -1, choices=albums)
  self.lista.SetFocus()
  self.lista.SetSelection(0)
  self.lista.SetSize(self.lista.GetBestSize())
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(self.lista, 0, wx.ALL, 5)
  goBtn = wx.Button(panel, wx.ID_OK)
  goBtn.SetDefault()
  cancelBtn = wx.Button(panel, wx.ID_CANCEL)
  btnSizer = wx.BoxSizer()
  btnSizer.Add(goBtn, 0, wx.ALL, 5)
  btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_string(self):
  return self.lista.GetStringSelection()

 def get_item(self):
  return self.lista.GetSelection()

 def get_response(self):
  return self.ShowModal()