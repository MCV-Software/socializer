# -*- coding: utf-8 -*-
import wx
import wx.adv
import application

class mainWindow(wx.Frame):
	def makeMenu(self):
		mb = wx.MenuBar()
		app_ = wx.Menu()
		create = wx.Menu()
		self.audio_album = create.Append(wx.NewId(), _("Audio album"))
		self.video_album = create.Append(wx.NewId(), _("Video album"))
		app_.Append(wx.NewId(), _("Create"), create)
		delete = wx.Menu()
		self.delete_audio_album = delete.Append(wx.NewId(), _("Audio album"))
		self.delete_video_album = delete.Append(wx.NewId(), _("Video album"))
		app_.Append(wx.NewId(), _("Delete"), delete)
		self.settings_dialog = app_.Append(wx.NewId(), _("Preferences"))
		me = wx.Menu()
		profile = wx.Menu()
		self.view_profile = profile.Append(wx.NewId(), _("View profile"))
#		self.edit_profile = profile.Append(wx.NewId(), _("Edit profile"))
		self.open_in_browser  = profile.Append(wx.NewId(), _("Open in browser"))
		me.Append(wx.NewId(), _("Profile"), profile)
		self.set_status = me.Append(wx.NewId(), _("Set status message"))
		buffer = wx.Menu()
		search = wx.Menu()
		self.search_audios = search.Append(wx.NewId(), _("Audio"))
		self.search_videos = search.Append(wx.NewId(), _("Video"))
		self.timeline = buffer.Append(wx.NewId(), _("&New timeline"))
		buffer.Append(wx.NewId(), _("Search"), search)
		self.update_buffer = buffer.Append(wx.NewId(), _("Update current buffer"))
		self.load_previous_items = buffer.Append(wx.NewId(), _("Load previous items"))
		self.remove_buffer_ = buffer.Append(wx.NewId(), _("&Remove buffer"))
		mb.Append(app_, _("Application"))
		mb.Append(me, _("Me"))
		mb.Append(buffer, _("Buffer"))
		player = wx.Menu()
		self.player_play = player.Append(wx.NewId(), _("Play/Pause"))
		self.player_play_all = player.Append(wx.NewId(), _("Play all"))
		self.player_previous = player.Append(wx.NewId(), _("Previous"))
		self.player_next = player.Append(wx.NewId(), _("Next"))
		self.player_shuffle = player.AppendCheckItem(wx.NewId(), _("Shuffle"))
		self.player_volume_up = player.Append(wx.NewId(), _("Volume up"))
		self.player_volume_down = player.Append(wx.NewId(), _("Volume down"))
		self.player_mute = player.Append(wx.NewId(), _("Mute"))
		help_ = wx.Menu()
		self.about = help_.Append(wx.NewId(), _("About {0}").format(application.name,))
		self.documentation = help_.Append(wx.NewId(), _("Manual"))
		self.check_for_updates = help_.Append(wx.NewId(), _("Check for updates"))
		self.changelog = help_.Append(wx.NewId(), _("Chan&gelog"))
		self.open_logs = help_.Append(wx.NewId(), _("Open logs directory"))
		self.open_config = help_.Append(wx.NewId(), _("Open config directory"))

		self.report = help_.Append(wx.NewId(), _("Report an error"))
		mb.Append(player, _("Audio player"))
		mb.Append(help_, _("Help"))
		self.SetMenuBar(mb)
		self.accel_tbl = wx.AcceleratorTable([
			# Assign keystrokes to control the player object.
			(wx.ACCEL_ALT, wx.WXK_LEFT, self.player_previous.GetId()),
			(wx.ACCEL_ALT, wx.WXK_RIGHT, self.player_next.GetId()),
			(wx.ACCEL_ALT, wx.WXK_DOWN, self.player_volume_down.GetId()),
			(wx.ACCEL_ALT, wx.WXK_UP, self.player_volume_up.GetId()),
			# Translators: Keystroke used to play/pause the current item in the playback queue. Use the latin alphabet, but you can match a different key here. For example if you want to assign this to the key "П", use G.
			(wx.ACCEL_CTRL, ord(_("P")), self.player_play.GetId()),
			(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord(_("P")), self.player_play_all.GetId()),
		])
		self.SetAcceleratorTable(self.accel_tbl)

	def __init__(self):
		super(mainWindow, self).__init__(parent=None, id=wx.NewId(), title=application.name)
		self.Maximize()
		self.makeMenu()
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sb = self.CreateStatusBar()
		self.tb = wx.Treebook(self.panel, -1)
		self.sizer.Add(self.tb, 1, wx.ALL|wx.EXPAND, 5)

	def realize(self):
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())
		self.Layout()
		self.SetSize(self.GetBestSize())

	def change_status(self, status):
		self.sb.SetStatusText(status)

	def connection_error(self):
		wx.MessageDialog(self, _("There is a connection error. Check your internet connection and try again later."), _("Connection error"), wx.ICON_ERROR).ShowModal()

	def get_buffer_count(self):
		return self.tb.GetPageCount()

	def add_buffer(self, buffer, name):
		self.tb.AddPage(buffer, name)

	def insert_buffer(self, buffer, name, pos):
		return self.tb.InsertSubPage(pos, buffer, name)

	def insert_chat_buffer(self, buffer, name, pos):
		return self.tb.InsertPage(pos, buffer, name)

	def search(self, name_):
		for i in range(0, self.tb.GetPageCount()):
			if self.tb.GetPage(i).name == name_: return i

	def get_current_buffer(self):
		return self.tb.GetCurrentPage()

	def get_current_buffer_pos(self):
		return self.tb.GetSelection()

	def get_buffer(self, pos):
		return self.GetPage(pos)

	def change_buffer(self, position):
		self.tb.ChangeSelection(position)

	def get_buffer_text(self, pos=None):
		if pos == None:
			pos = self.tb.GetSelection()
		return self.tb.GetPageText(pos)

	def get_buffer_by_id(self, id):
		return self.nb.FindWindowById(id)

	def advance_selection(self, forward):
		self.tb.AdvanceSelection(forward)

	def about_dialog(self, *args, **kwargs):
		info = wx.adv.AboutDialogInfo()
		info.SetName(application.name)
		info.SetVersion(application.version)
		info.SetDescription(application.description)
		info.SetCopyright(application.copyright)
		info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
		info.AddDeveloper(application.author)
		wx.adv.AboutBox(info)

	def remove_buffer(self, pos):
		self.tb.DeletePage(pos)

	def remove_buffer_from_position(self, pos):
		return self.tb.RemovePage(pos)

	def notify(self, title, text):
		self.notification = wx.adv.NotificationMessage(title=title, message=text, parent=self)
		self.notification.Show()