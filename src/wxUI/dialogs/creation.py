import wx
import widgetUtils

class audio_album(widgetUtils.BaseDialog):

	def __init__(self, *args, **kwargs):
		super(audio_album, self).__init__(title=_(u"Create a new album"), parent=None)
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl = wx.StaticText(panel, wx.NewId(), _(u"Album title"))
		self.title = wx.TextCtrl(panel, wx.NewId())
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl, 1, wx.ALL, 5)
		box.Add(self.title, 1, wx.ALL, 5)
		sizer.Add(box, 1, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
		ok.SetDefault()
		cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
		btnsizer = wx.BoxSizer()
		btnsizer.Add(ok, 0, wx.ALL, 5)
		btnsizer.Add(cancel, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())