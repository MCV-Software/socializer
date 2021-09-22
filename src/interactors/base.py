# -*- coding: utf-8 -*-
from pubsub import pub

class baseInteractor(object):

    def install(self, view, presenter, modulename):
        self.modulename = modulename
        self.view = view
        self.presenter = presenter
        pub.subscribe(self.disable_control, "{modulename}_disable_control".format(modulename=modulename))
        pub.subscribe(self.enable_control, "{modulename}_enable_control".format(modulename=modulename))
        pub.subscribe(self.set_label, "{modulename}_set_label".format(modulename=modulename))
        pub.subscribe(self.focus_control, "{modulename}_focus_control".format(modulename=modulename))
        pub.subscribe(self.set_title, "{modulename}_set_title".format(modulename=modulename))

    def uninstall(self):
        pub.unsubscribe(self.disable_control, "{modulename}_disable_control".format(modulename=self.modulename))
        pub.unsubscribe(self.enable_control, "{modulename}_enable_control".format(modulename=self.modulename))
        pub.unsubscribe(self.set_label, "{modulename}_set_label".format(modulename=self.modulename))
        pub.unsubscribe(self.focus_control, "{modulename}_focus_control".format(modulename=self.modulename))
        pub.unsubscribe(self.set_title, "{modulename}_set_title".format(modulename=self.modulename))
        self.view.Destroy()

    def start(self):
        self.result = self.view.get_response()

    def disable_control(self, control):
        self.view.disable(control)

    def enable_control(self, control):
        self.view.enable(control)

    def focus_control(self, control):
        getattr(self.view, control).SetFocus()

    def set_label(self, control, label):
        self.view.set(control, label)

    def set_title(self, value):
        self.view.SetTitle(value)
