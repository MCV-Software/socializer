# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
import wx
import widgetUtils
from pubsub import pub
from views.dialogs import urlList
from . import base

class userProfileInteractor(base.baseInteractor):

	def enable_control(self, tab, control):
		if not hasattr(self.view, tab):
			raise AttributeError("The viw does not contain the specified tab.")
		tab = getattr(self.view, tab)
		if not hasattr(tab, control):
			raise AttributeError("The control is not present in the tab.")
		getattr(tab, control).Enable(True)

	def set(self, tab, control, value):
		if not hasattr(self.view, tab):
			raise AttributeError("The viw does not contain the specified tab.")
		tab = getattr(self.view, tab)
		if not hasattr(tab, control):
			raise AttributeError("The control is not present in the tab.")
		control = getattr(tab, control)
		control.SetValue(value)

	def set_label(self, tab, control, value):
		if not hasattr(self.view, tab):
			raise AttributeError("The viw does not contain the specified tab.")
		tab = getattr(self.view, tab)
		if not hasattr(tab, control):
			raise AttributeError("The control is not present in the tab.")
		control = getattr(tab, control)
		control.SetLabel(value)

	def load_image(self, image):
		image = wx.Image(stream=six.BytesIO(image.content))
		try:
			self.view.image.SetBitmap(wx.Bitmap(image))
		except ValueError:
			return
		self.view.panel.Layout()

	def install(self, *args, **kwargs):
		super(userProfileInteractor, self).install(*args, **kwargs)
		pub.subscribe(self.set, self.modulename+"_set")
		pub.subscribe(self.load_image, self.modulename+"_load_image")
		self.view.create_controls("main_info")
		self.view.realice()
		widgetUtils.connect_event(self.view.main_info.go_site, widgetUtils.BUTTON_PRESSED, self.on_visit_website)

	def uninstall(self):
		super(userProfileInteractor, self).uninstall()
		pub.unsubscribe(self.set, self.modulename+"_set")
		pub.unsubscribe(self.load_image, self.modulename+"_load_image")


	def on_visit_website(self, *args, **kwargs):
		urls = self.presenter.get_urls()
		if len(urls) == 1:
			self.presenter.visit_url(urls[0])
		else:
			dialog = urlList.urlList()
			dialog.populate_list(urls)
			if dialog.get_response() != widgetUtils.OK:
				return
			selected_url = urls[dialog.get_item()]
			self.presenter.visit_url(selected_url)