# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx
import widgetUtils

class general(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel, languages):
		super(general, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		langBox = wx.StaticBoxSizer(parent=self, orient=wx.HORIZONTAL, label=_("Language"))
		self.language = wx.ListBox(langBox.GetStaticBox(), wx.NewId(), choices=languages)
		self.language.SetSize(self.language.GetBestSize())
		langBox.Add(self.language, 0, wx.ALL, 5)
		sizer.Add(langBox, 0, wx.ALL, 5)
		lbl1 = wx.StaticText(self, wx.NewId(), _("Number of items to load for newsfeed and wall buffers (maximun 100)"))
		self.wall_buffer_count = wx.SpinCtrl(self, wx.NewId())
		self.wall_buffer_count.SetRange(1, 100)
		box1 = wx.BoxSizer(wx.HORIZONTAL)
		box1.Add(lbl1, 0, wx.ALL, 5)
		box1.Add(self.wall_buffer_count, 0, wx.ALL, 5)
		sizer.Add(box1, 0, wx.ALL, 5)
		lbl3 = wx.StaticText(self, wx.NewId(), _("Number of items to load in video buffers (maximun 200)"))
		self.video_buffers_count = wx.SpinCtrl(self, wx.NewId())
		self.video_buffers_count.SetRange(1, 200)
		box3 = wx.BoxSizer(wx.HORIZONTAL)
		box3.Add(lbl3, 0, wx.ALL, 5)
		box3.Add(self.video_buffers_count, 0, wx.ALL, 5)
		sizer.Add(box3, 0, wx.ALL, 5)
		self.load_images = wx.CheckBox(self, wx.NewId(), _("Load images in posts"))
		sizer.Add(self.load_images, 0, wx.ALL, 5)
		self.use_proxy = wx.CheckBox(self, wx.NewId(), _("Use proxy"))
		sizer.Add(self.use_proxy, 0, wx.ALL, 5)
		lbl4 = wx.StaticText(self, wx.NewId(), _("Update channel"))
		self.update_channel = wx.ComboBox(self, wx.NewId(), choices=[_("Stable"), _("Alpha")], value=_("Native"), style=wx.CB_READONLY)
		box4 = wx.BoxSizer(wx.HORIZONTAL)
		box4.Add(lbl4, 0, wx.ALL, 5)
		box4.Add(self.update_channel, 0, wx.ALL, 5)
		sizer.Add(box4, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class chat(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel):
		super(chat, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.notify_online = wx.CheckBox(self, wx.NewId(), _("Show notifications when users are online"))
		sizer.Add(self.notify_online, 0, wx.ALL, 5)
		self.notify_offline = wx.CheckBox(self, wx.NewId(), _("Show notifications when users are offline"))
		sizer.Add(self.notify_offline, 0, wx.ALL, 5)
		lbl = wx.StaticText(self, wx.NewId(), _("Notification type"))
		self.notifications = wx.ComboBox(self, wx.NewId(), choices=[_("Native"), _("Custom"),], value=_("Native"), style=wx.CB_READONLY)
		nbox = wx.BoxSizer(wx.HORIZONTAL)
		nbox.Add(lbl, 0, wx.ALL, 5)
		nbox.Add(self.notifications, 0, wx.ALL, 5)
		sizer.Add(nbox, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class loadAtStartup(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel):
		super(loadAtStartup, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.audio_albums = wx.CheckBox(self, wx.NewId(), _("Create buffers for audio albums at startup"))
		sizer.Add(self.audio_albums, 0, wx.ALL, 5)
		self.video_albums = wx.CheckBox(self, wx.NewId(), _("Create buffers for video albums at startup"))
		sizer.Add(self.video_albums, 0, wx.ALL, 5)
		self.communities = wx.CheckBox(self, wx.NewId(), _("Create buffers for communities and public pages at startup"))
		sizer.Add(self.communities, 0, wx.ALL, 5)
		self.SetSizer(sizer)

class sound(wx.Panel, widgetUtils.BaseDialog):
	def __init__(self, panel, input_devices, output_devices, soundpacks):
		super(sound, self).__init__(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		output_label = wx.StaticText(self, wx.NewId(), _("Output device"))
		self.output = wx.ComboBox(self, wx.NewId(), choices=output_devices, style=wx.CB_READONLY)
		self.output.SetSize(self.output.GetBestSize())
		outputBox = wx.BoxSizer(wx.HORIZONTAL)
		outputBox.Add(output_label, 0, wx.ALL, 5)
		outputBox.Add(self.output, 0, wx.ALL, 5)
		sizer.Add(outputBox, 0, wx.ALL, 5)
		input_label = wx.StaticText(self, wx.NewId(), _("Input device"))
		self.input = wx.ComboBox(self, wx.NewId(), choices=input_devices, style=wx.CB_READONLY)
		self.input.SetSize(self.input.GetBestSize())
		inputBox = wx.BoxSizer(wx.HORIZONTAL)
		inputBox.Add(input_label, 0, wx.ALL, 5)
		inputBox.Add(self.input, 0, wx.ALL, 5)
		sizer.Add(inputBox, 0, wx.ALL, 5)
#		soundBox =  wx.BoxSizer(wx.VERTICAL)
#		soundpack_label = wx.StaticText(self, wx.NewId(), _(u"Sound pack"))
#		self.soundpack = wx.ComboBox(self, -1, choices=soundpacks, style=wx.CB_READONLY)
#		self.soundpack.SetSize(self.soundpack.GetBestSize())
#		soundBox.Add(soundpack_label, 0, wx.ALL, 5)
#		soundBox.Add(self.soundpack, 0, wx.ALL, 5)
#		sizer.Add(soundBox, 0, wx.ALL, 5)
		self.SetSizer(sizer)

	def on_keypress(self, event, *args, **kwargs):
		""" Invert movement of up and down arrow keys when dealing with a wX Slider.
		See https://github.com/manuelcortez/TWBlue/issues/261
		and http://trac.wxwidgets.org/ticket/2068
		"""
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_UP:
			return self.volumeCtrl.SetValue(self.volumeCtrl.GetValue()+1)
		elif keycode == wx.WXK_DOWN:
			return self.volumeCtrl.SetValue(self.volumeCtrl.GetValue()-1)
		event.Skip()

	def get(self, control):
		return getattr(self, control).GetStringSelection()

class configurationDialog(widgetUtils.BaseDialog):

	def __init__(self, title):
		super(configurationDialog, self).__init__(None, -1, title=title)
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.notebook = wx.Notebook(self.panel)

	def create_general(self, languages):
		self.general = general(self.notebook, languages)
		self.notebook.AddPage(self.general, _("General"))
		self.general.SetFocus()

	def create_chat(self):
		self.chat = chat(self.notebook)
		self.notebook.AddPage(self.chat, _("Chat settings"))

	def create_startup_options(self):
		self.startup = loadAtStartup(self.notebook)
		self.notebook.AddPage(self.startup, _("Optional buffers"))

	def create_sound(self, input_devices, output_devices, soundpacks):
		self.sound = sound(self.notebook, input_devices, output_devices, soundpacks)
		self.notebook.AddPage(self.sound, _("Sound settings"))

	def realize(self):
		self.sizer.Add(self.notebook, 0, wx.ALL, 5)
		ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
		ok = wx.Button(self.panel, wx.ID_OK, _("Save"))
		ok.SetDefault()
		cancel = wx.Button(self.panel, wx.ID_CANCEL, _("Close"))
		self.SetEscapeId(cancel.GetId())
		ok_cancel_box.Add(ok, 0, wx.ALL, 5)
		ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
		self.sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def get_value(self, panel, key):
		p = getattr(self, panel)
		return getattr(p, key).GetValue()

	def set_value(self, panel, key, value):
		p = getattr(self, panel)
		control = getattr(p, key)
		getattr(control, "SetValue")(value)

	def alpha_channel(self):
		return wx.MessageDialog(self, _("The alpha channel contains bleeding edge changes introduced to Socializer. A new alpha update is generated every time there are new changes in the project. Take into account that updates are generated automatically and may fail at any time due to errors in the build process. Use alpha channels when you are sure you want to try the latest changes and contribute with reports to fix bugs. Never use alpha channel updates for everyday use. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

	def weekly_channel(self):
		return wx.MessageDialog(self, _("The weekly channel generates an update automatically every week by building the source code present in the project. This version is used to test features added to the next stable version. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()