# -*- coding: utf-8 -*-
import wx
import widgetUtils

class displayBasicPost(widgetUtils.BaseDialog):
	def __init__(self, *args, **kwargs):
		super(displayBasicPost, self).__init__(parent=None, *args, **kwargs)
		self.panel = wx.Panel(self, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)

	def done(self):
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def create_post_view(self, label=_("Message")):
		lbl = wx.StaticText(self.panel, -1, label)
		self.post_view = wx.TextCtrl(self.panel, -1, size=(730, -1), style=wx.TE_READONLY|wx.TE_MULTILINE)
		selectId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
		self.accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('A'), selectId),])
		self.SetAcceleratorTable(self.accel_tbl)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.post_view, 0, wx.ALL, 5)
		return box

	def onSelect(self, event):
		self.post_view.SelectAll()

	def create_views_control(self):
		lbl = wx.StaticText(self.panel, -1, _("Views"))
		self.views = wx.TextCtrl(self.panel, -1, style=wx.TE_READONLY|wx.TE_MULTILINE)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.views, 0, wx.ALL, 5)
		return box


	def create_comments_list(self):
		lbl = wx.StaticText(self.panel, -1, _("Comments"))
		self.comments = widgetUtils.list(self.panel, _("User"), _("Comment"), _("Date"), _("Likes"), style=wx.LC_REPORT)
		self.reply = wx.Button(self.panel, -1, _("Reply to comment"))
		self.reply.Enable(False)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.comments.list, 0, wx.ALL, 5)
		box.Add(self.reply, 0, wx.ALL, 5)
		return box

	def create_attachments(self):
		lbl = wx.StaticText(self.panel, -1, _("Attachments"))
		self.attachments = widgetUtils.list(self.panel, _("Type"), _("Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		return box

	def create_photo_viewer(self):
		self.image = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap(1280, 860), size=(604, 604))
		self.sizer.Add(self.image, 1, wx.ALL, 10)
		self.previous_photo = wx.Button(self.panel, wx.NewId(), _("Previous photo"))
		self.view_photo = wx.Button(self.panel, wx.NewId(), _("View in full screen"))
		self.next_photo = wx.Button(self.panel, wx.NewId(), _("Next photo"))
		actionsS = wx.BoxSizer(wx.HORIZONTAL)
		actionsS.Add(self.previous_photo, 0, wx.ALL, 5)
		actionsS.Add(self.view_photo, 0, wx.ALL, 5)
		actionsS.Add(self.next_photo, wx.ALL, 5)
		self.previous_photo.Enable(False)
		self.view_photo.Enable(False)
		self.next_photo.Enable(False)
		self.sizer.Add(actionsS, 0, wx.ALL, 5)

	def enable_photo_controls(self, navigation=True):
		self.view_photo.Enable(True)
		if navigation:
			self.previous_photo.Enable(True)
			self.next_photo.Enable(True)

	def create_likes_box(self):
		self.likes = wx.Button(self.panel, -1, _("Loading data..."))
		return self.likes

	def create_shares_box(self):
		self.shares = wx.Button(self.panel, -1, _("Loading data..."))
		return self.shares

	def create_action_buttons(self, comment=True):
		self.like = wx.Button(self.panel, -1, _("&Like"))
		self.repost = wx.Button(self.panel, -1, _("Repost"))
		if comment: self.comment = wx.Button(self.panel, -1, _("Add comment"))
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(self.like, 0, wx.ALL, 5)
		box.Add(self.repost, 0, wx.ALL, 5)
		if comment: box.Add(self.comment, 0, wx.ALL, 5)
		return box

	def create_tools_button(self):
		self.tools = wx.Button(self.panel, -1, _("Actions"))

	def create_dialog_buttons(self):
		self.close = wx.Button(self.panel, wx.ID_CANCEL, _("Close"))
		return self.close

	def set_post(self, text):
		if hasattr(self, "post_view"):
			self.post_view.ChangeValue(text)
		else:
			return False

	def insert_comments(self, comments):
		for i in comments:
			self.comments.insert_item(False, *i)

	def insert_attachments(self, attachments):
		for i in attachments:
			self.attachments.insert_item(False, *i)

	def set_likes(self, likes):
		if hasattr(self, "likes"):
			self.likes.SetLabel(_("{0} people like this").format(likes,))
		else:
			return False

	def set_shares(self, shares):
		if hasattr(self, "shares"):
			self.shares.SetLabel(_("Shared {0} times").format(shares,))
		else:
			return False

class displayPost(displayBasicPost):
	def __init__(self, *args, **kwargs):
		super(displayPost, self).__init__(*args, **kwargs)
		post_view_box = self.create_post_view()
		self.sizer.Add(post_view_box, 0, wx.ALL, 5)
		views_box = self.create_views_control()
		self.sizer.Add(views_box, 0, wx.ALL, 5)
		attachments_box = self.create_attachments()
		self.sizer.Add(attachments_box, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		self.create_photo_viewer()
		self.image.Enable(False)
		self.create_tools_button()
		self.sizer.Add(self.tools, 0, wx.ALL, 5)
		likes_box = self.create_likes_box()
		self.sizer.Add(likes_box, 0, wx.ALL, 5)
		shares_box = self.create_shares_box()
		self.sizer.Add(shares_box, 0, wx.ALL, 5)
		actions_box = self.create_action_buttons()
		self.sizer.Add(actions_box, 0, wx.ALL, 5)
		comments_box = self.create_comments_list()
		self.sizer.Add(comments_box, 0, wx.ALL, 5)
		self.sizer.Add(self.create_dialog_buttons())
		self.done()

class displayComment(displayBasicPost):
	def __init__(self, *args, **kwargs):
		super(displayComment, self).__init__(*args, **kwargs)
		post_view_box = self.create_post_view()
		self.sizer.Add(post_view_box, 0, wx.ALL, 5)
		attachments_box = self.create_attachments()
		self.sizer.Add(attachments_box, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		self.create_photo_viewer()
		self.image.Enable(False)
		self.create_tools_button()
		self.sizer.Add(self.tools, 0, wx.ALL, 5)
		likes_box = self.create_likes_box()
		self.sizer.Add(likes_box, 0, wx.ALL, 5)
		actions_box = self.create_action_buttons()
		self.sizer.Add(actions_box, 0, wx.ALL, 5)
		self.sizer.Add(self.create_dialog_buttons())
		self.done()

	def create_action_buttons(self, comment=True):
		self.like = wx.Button(self.panel, -1, _("&Like"))
		self.reply = wx.Button(self.panel, -1, _("Reply"))
		if comment: self.comment = wx.Button(self.panel, -1, _("Add comment"))
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(self.like, 0, wx.ALL, 5)
		box.Add(self.reply, 0, wx.ALL, 5)
		if comment: box.Add(self.comment, 0, wx.ALL, 5)
		return box

class displayTopic(displayBasicPost):
	def __init__(self, *args, **kwargs):
		super(displayTopic, self).__init__(*args, **kwargs)
		comments_box = self.create_comments_list()
		self.sizer.Add(comments_box, 0, wx.ALL, 5)
		attachments_box = self.create_attachments()
		self.sizer.Add(attachments_box, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		self.create_photo_viewer()
		self.image.Enable(False)
		self.create_tools_button()
		self.sizer.Add(self.tools, 0, wx.ALL, 5)
		actions_box = self.create_action_buttons()
		self.sizer.Add(actions_box, 0, wx.ALL, 5)
		self.sizer.Add(self.create_dialog_buttons())
		self.done()

	def create_action_buttons(self, comment=True):
		self.like = wx.Button(self.panel, -1, _("&Like"))
		if comment: self.comment = wx.Button(self.panel, -1, _("Add comment"))
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(self.like, 0, wx.ALL, 5)
		if comment: box.Add(self.comment, 0, wx.ALL, 5)
		return box

	def create_comments_list(self):
		lbl = wx.StaticText(self.panel, -1, _("Posts"))
		self.comments = widgetUtils.list(self.panel, _("User"), _("Comment"), _("Date"), _("Likes"), style=wx.LC_REPORT)
		self.load_more_comments = wx.Button(self.panel, wx.NewId(), _("Load previous comments"))
		self.reply = wx.Button(self.panel, -1, _("Reply"))
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.comments.list, 0, wx.ALL, 5)
		box.Add(self.reply, 0, wx.ALL, 5)
		return box

class displayAudio(widgetUtils.BaseDialog):
	def __init__(self, *args, **kwargs):
		super(displayAudio, self).__init__(parent=None, *args, **kwargs)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl_list = wx.StaticText(panel, wx.NewId(), _("Audio &files"))
		self.list = wx.ListBox(panel, wx.NewId())
		listS = wx.BoxSizer(wx.HORIZONTAL)
		listS.Add(lbl_list, 0, wx.ALL, 5)
		listS.Add(self.list, 0, wx.ALL, 5)
		sizer.Add(listS, 0, wx.ALL, 5)
		lbl_title = wx.StaticText(panel, wx.NewId(), _("&Title"))
		self.title = wx.TextCtrl(panel, wx.NewId(), size=(413, -1), style=wx.TE_READONLY|wx.TE_MULTILINE)
		titleBox = wx.BoxSizer(wx.HORIZONTAL)
		titleBox.Add(lbl_title, 0, wx.ALL, 5)
		titleBox.Add(self.title, 0, wx.ALL, 5)
		sizer.Add(titleBox, 0, wx.ALL, 5)
		lbl_artist = wx.StaticText(panel, wx.NewId(), _("&Artist"))
		self.artist = wx.TextCtrl(panel, wx.NewId(), size=(413, -1), style=wx.TE_READONLY|wx.TE_MULTILINE)
		artistBox = wx.BoxSizer(wx.HORIZONTAL)
		artistBox.Add(lbl_artist, 0, wx.ALL, 5)
		artistBox.Add(self.artist, 0, wx.ALL, 5)
		sizer.Add(artistBox, 0, wx.ALL, 5)
		lbl_duration = wx.StaticText(panel, wx.NewId(), _("&Duration"))
		self.duration = wx.TextCtrl(panel, wx.NewId(), size=(413, -1), style=wx.TE_READONLY|wx.TE_MULTILINE)
		durationBox = wx.BoxSizer(wx.HORIZONTAL)
		durationBox.Add(lbl_duration, 0, wx.ALL, 5)
		durationBox.Add(self.duration, 0, wx.ALL, 5)
		sizer.Add(durationBox, 0, wx.ALL, 5)
		lbl_lyrics = wx.StaticText(panel, wx.NewId(), _("&Lyric"))
		self.lyric = wx.TextCtrl(panel, wx.NewId(), size=(500, 500), style=wx.TE_READONLY|wx.TE_MULTILINE)
		lbox = wx.BoxSizer(wx.HORIZONTAL)
		lbox.Add(lbl_lyrics, 0, wx.ALL, 5)
		lbox.Add(self.lyric, 0, wx.ALL, 5)
		sizer.Add(lbox, 0, wx.ALL, 5)
		self.play = wx.Button(panel, wx.NewId(), _("&Play"))
		self.download = wx.Button(panel, wx.NewId(), _("&Download"))
		self.add = wx.Button(panel, wx.NewId(), _("&Add to your library"))
		self.remove = wx.Button(panel, wx.NewId(), _("&Remove from your library"))
		self.add.Enable(False)
		self.remove.Enable(False)
		close = wx.Button(panel, wx.ID_CANCEL)
		bbox = wx.BoxSizer(wx.HORIZONTAL)
		bbox.Add(self.play, 0, wx.ALL, 5)
		bbox.Add(self.download, 0, wx.ALL, 5)
		bbox.Add(self.add, 0, wx.ALL, 5)
		bbox.Add(self.remove, 0, wx.ALL, 5)
		bbox.Add(close, 0, wx.ALL, 5)

	def change_state(self, button_name, state):
		getattr(self, button_name).Enable(state)

	def get_destination_path(self, filename):
		saveFileDialog = wx.FileDialog(self, _("Save this file"), "", filename, _("Audio Files(*.mp3)|*.mp3"), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if saveFileDialog.ShowModal() == wx.ID_OK:
			return saveFileDialog.GetPath()
		saveFileDialog.Destroy()

	def insert_audio(self, audio_):
		self.list.Append(audio_)

	def get_audio(self):
		return self.list.GetSelection()

class displayArticle(widgetUtils.BaseDialog):
	def __init__(self, *args, **kwargs):
		super(displayArticle, self).__init__(parent=None, *args, **kwargs)
		self.panel = wx.Panel(self, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		article_view_box = self.create_article_view()
		self.sizer.Add(article_view_box, 0, wx.ALL, 5)
		views_box = self.create_views_control()
		self.sizer.Add(views_box, 0, wx.ALL, 5)
		attachments_box = self.create_attachments()
		self.sizer.Add(attachments_box, 0, wx.ALL, 5)
		self.attachments.list.Enable(False)
		self.create_tools_button()
		self.sizer.Add(self.tools, 0, wx.ALL, 5)
		self.sizer.Add(self.create_dialog_buttons())
		self.done()

	def done(self):
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

	def create_article_view(self, label=_("Article")):
		lbl = wx.StaticText(self.panel, -1, label)
		self.article_view = wx.TextCtrl(self.panel, -1, size=(730, -1), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.BORDER_SIMPLE)
		selectId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
		self.accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('A'), selectId),])
		self.SetAcceleratorTable(self.accel_tbl)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.article_view, 0, wx.ALL, 5)
		return box

	def onSelect(self, event):
		self.article_view.SelectAll()

	def create_views_control(self):
		lbl = wx.StaticText(self.panel, -1, _("Views"))
		self.views = wx.TextCtrl(self.panel, -1, style=wx.TE_READONLY|wx.TE_MULTILINE)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.views, 0, wx.ALL, 5)
		return box

	def create_tools_button(self):
		self.tools = wx.Button(self.panel, -1, _("Actions"))

	def create_dialog_buttons(self):
		self.close = wx.Button(self.panel, wx.ID_CANCEL, _("Close"))
		return self.close

	def create_attachments(self):
		lbl = wx.StaticText(self.panel, -1, _("Attachments"))
		self.attachments = widgetUtils.list(self.panel, _("Type"), _("Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		return box

	def set_article(self, text):
		if hasattr(self, "article_view"):
			self.article_view.ChangeValue(text)
		else:
			return False

	def insert_attachments(self, attachments):
		for i in attachments:
			self.attachments.insert_item(False, *i)

class displayFriendship(widgetUtils.BaseDialog):
	def __init__(self):
		super(displayFriendship, self).__init__(parent=None)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.friends = widgetUtils.list(panel, [_("Friend")], style=wx.LC_REPORT)
		sizer.Add(self.friends.list, 0, wx.ALL, 5)
		close = wx.Button(panel, wx.ID_CANCEL)
		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		btnbox.Add(close, 0, wx.ALL, 5)
		sizer.Add(btnbox, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

class displayPoll(widgetUtils.BaseDialog):

	def __init__(self, question="", *args, **kwargs):
		super(displayPoll, self).__init__(parent=None, *args, **kwargs)
		self.panel = wx.Panel(self, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(self.panel, wx.NewId(), _("Question"))
		self.question = wx.TextCtrl(self.panel, wx.NewId(), question, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(730, -1))
		self.sizer.Add(label, 0, wx.ALL, 5)
		self.sizer.Add(self.question, 0, wx.ALL, 5)

	def add_options(self, options, multiple=False):
		if not isinstance(options[0], str):
			return self.add_results(options)
		self.options = []
		sizer = wx.StaticBoxSizer(parent=self.panel, orient=wx.VERTICAL, label=_("Options"))
		for i in options:
			if multiple == False:
				if len(self.options) == 0:
					control = wx.RadioButton(sizer.GetStaticBox(), wx.NewId(), i, style=wx.RB_GROUP)
				else:
					control = wx.RadioButton(sizer.GetStaticBox(), wx.NewId(), i)
			else:
				control = wx.CheckBox(sizer.GetStaticBox(), wx.NewId(), i)
			self.options.append(control)
			sizer.Add(control, 0, wx.ALL, 5)
		self.sizer.Add(sizer, 0, wx.ALL, 5)

	def get_answers(self):
		answers = []
		for i in self.options:
			answers.append(i.GetValue())
		return answers

	def add_results(self, options):
		sizer = wx.StaticBoxSizer(parent=self.panel, orient=wx.VERTICAL, label=_("Poll results"))
		for i in options:
			sizer2 = wx.StaticBoxSizer(parent=sizer.GetStaticBox(), orient=wx.HORIZONTAL, label=i[0])
			staticcontrol = wx.StaticText(sizer2.GetStaticBox(), wx.NewId(), i[0])
			control = wx.TextCtrl(sizer2.GetStaticBox(), wx.NewId(), _("{votes} ({rate}%)").format(votes=i[1], rate=i[2]), style=wx.TE_READONLY|wx.TE_MULTILINE)
			sizer2.Add(staticcontrol, 0, wx.ALL, 5)
			sizer2.Add(control, 0, wx.ALL, 5)
			sizer.Add(sizer2, 0, wx.ALL, 5)
		self.sizer.Add(sizer, 0, wx.ALL, 5)

	def done(self):
		self.ok = wx.Button(self.panel, wx.ID_OK, _("Vote"))
		cancel = wx.Button(self.panel, wx.ID_CANCEL)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.ok, 0, wx.ALL, 5)
		sizer.Add(cancel, 0, wx.ALL, 5)
		self.panel.SetSizer(self.sizer)
		self.SetClientSize(self.sizer.CalcMin())

