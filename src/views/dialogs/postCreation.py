# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class createTextMessage(widgetUtils.BaseDialog):
    def __init__(self, *args, **kwargs):
        super(createTextMessage, self).__init__(parent=None, *args, **kwargs)

    def createTextArea(self, message="", text=""):
        self.panel = wx.Panel(self)
        self.label = wx.StaticText(self.panel, -1, message)
        self.text = wx.TextCtrl(self.panel, -1, text, size=(439, -1), style=wx.TE_MULTILINE)
        self.text.SetFocus()
        self.textBox = wx.BoxSizer(wx.HORIZONTAL)
        self.textBox.Add(self.label, 0, wx.ALL, 5)
        self.textBox.Add(self.text, 0, wx.ALL, 5)

    def create_privacy_box(self):
        lbl = wx.StaticText(self.panel, wx.NewId(), _("&Privacy"))
        self.privacy = wx.ComboBox(self.panel, wx.NewId(), choices=[_("All users"), _("Friends of friends"),], value=_("All users"), style=wx.CB_READONLY)
        self.privacyBox = wx.BoxSizer(wx.HORIZONTAL)
        self.privacyBox.Add(lbl, 0, wx.ALL, 5)
        self.privacyBox.Add(self.privacy, 0, wx.ALL, 5)

    def text_focus(self):
        self.text.SetFocus()

    def get_text(self):
        return self.text.GetValue()

    def set_text(self, text):
        return self.text.ChangeValue(text)

    def enable_button(self, buttonName):
        if getattr(self, buttonName):
            return getattr(self, buttonName).Enable()

    def disable_button(self, buttonName):
        if getattr(self, buttonName):
            return getattr(self, buttonName).Disable()

    def onSelect(self, ev):
        self.text.SelectAll()

    def set_cursor_at_end(self):
        self.text.SetInsertionPoint(len(self.text.GetValue()))

    def set_cursor_at_position(self, position):
        self.text.SetInsertionPoint(position)

    def get_position(self):
        return self.text.GetInsertionPoint()

class createPostDialog(createTextMessage):
    def createControls(self, title, message,  text, mode):
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.createTextArea(message, text)
        self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
        if mode == "post":
            self.create_privacy_box()
            self.mainBox.Add(self.privacyBox, 0, wx.ALL, 5)
        self.attach = wx.Button(self.panel, -1, _("Attach"), size=wx.DefaultSize)
        self.mention = wx.Button(self.panel, wx.NewId(), _("Tag a friend"))
        self.spellcheck = wx.Button(self.panel, -1, _("Spelling &correction"), size=wx.DefaultSize)
        self.translateButton = wx.Button(self.panel, -1, _("&Translate message"), size=wx.DefaultSize)
        self.okButton = wx.Button(self.panel, wx.ID_OK, _("Send"), size=wx.DefaultSize)
        self.okButton.SetDefault()
        cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("Close"), size=wx.DefaultSize)
        self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsBox1.Add(self.attach, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.mention, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.translateButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 10)
        self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 10)
        self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.ok_cancelSizer)
        selectId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
        self.accel_tbl = wx.AcceleratorTable([
                (wx.ACCEL_CTRL, ord('A'), selectId),])
        self.SetAcceleratorTable(self.accel_tbl)
        self.panel.SetSizer(self.mainBox)
        self.SetTitle(title)

    def __init__(self, title, message, text, mode="post"):
        super(createPostDialog, self).__init__()
        self.createControls(title, message, text, mode)
        self.SetClientSize(self.mainBox.CalcMin())

class createCommentDialog(createTextMessage):
    def createControls(self, title, message,  text, **kwargs):
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.createTextArea(message, text)
        self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
        self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
        self.mention = wx.Button(self.panel, wx.NewId(), _("Tag a friend"))
        self.translateButton = wx.Button(self.panel, -1, _("Translate message"), size=wx.DefaultSize)
        self.okButton = wx.Button(self.panel, wx.ID_OK, _("Send"), size=wx.DefaultSize)
        self.okButton.SetDefault()
        cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("Close"), size=wx.DefaultSize)
        self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.mention, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.translateButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 10)
        self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 10)
        self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.ok_cancelSizer)
        selectId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('A'), selectId),])
        self.SetAcceleratorTable(self.accel_tbl)
        self.panel.SetSizer(self.mainBox)
        self.SetTitle(title)

    def __init__(self, title, message, text, *args, **kwargs):
        super(createCommentDialog, self).__init__()
        self.createControls(message, title, text, **kwargs)
        self.SetClientSize(self.mainBox.CalcMin())
        self.SetTitle(title)

class createTopicDialog(createCommentDialog):
    def createTextArea(self, message="", text="", topic_title=""):
        self.panel = wx.Panel(self)
        label = wx.StaticText(self.panel, -1, _("Title"))
        self.title = wx.TextCtrl(self.panel, wx.NewId(), topic_title)
        label2 = wx.StaticText(self.panel, -1, _("Message"))
        self.text = wx.TextCtrl(self.panel, -1, text, size=(439, -1), style=wx.TE_MULTILINE)
        self.title.SetFocus()
        self.textBox = wx.BoxSizer(wx.VERTICAL)
        titleb = wx.BoxSizer(wx.HORIZONTAL)
        titleb.Add(label, 0, wx.ALL, 5)
        titleb.Add(self.title, 0, wx.ALL, 5)
        self.textBox.Add(titleb, 0, wx.ALL, 5)
        textb = wx.BoxSizer(wx.HORIZONTAL)
        textb.Add(label2, 0, wx.ALL, 5)
        textb.Add(self.text, 0, wx.ALL, 5)
        self.textBox.Add(textb, 0, wx.ALL, 5)

    def createControls(self, title, message,  text, topic_title):
        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.createTextArea(message, text, topic_title)
        self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
        self.attach = wx.Button(self.panel, -1, _("Attach"), size=wx.DefaultSize)
        self.mention = wx.Button(self.panel, wx.NewId(), _("Tag a friend"))
        self.spellcheck = wx.Button(self.panel, -1, _("Spelling &correction"), size=wx.DefaultSize)
        self.translateButton = wx.Button(self.panel, -1, _("&Translate message"), size=wx.DefaultSize)
        self.okButton = wx.Button(self.panel, wx.ID_OK, _("Send"), size=wx.DefaultSize)
        self.okButton.SetDefault()
        cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("Close"), size=wx.DefaultSize)
        self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsBox1.Add(self.attach, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.mention, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 10)
        self.buttonsBox1.Add(self.translateButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 10)
        self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 10)
        self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 10)
        self.mainBox.Add(self.ok_cancelSizer)
        selectId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
        self.accel_tbl = wx.AcceleratorTable([
                (wx.ACCEL_CTRL, ord('A'), selectId),])
        self.SetAcceleratorTable(self.accel_tbl)
        self.panel.SetSizer(self.mainBox)
