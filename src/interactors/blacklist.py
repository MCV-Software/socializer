# -*- coding: utf-8 -*-
import widgetUtils
from wxUI import commonMessages
from pubsub import pub
from . import base

class blacklistInteractor(base.baseInteractor):

    def add_items(self, control, items):
        if not hasattr(self.view, control):
            raise AttributeError("The control is not present in the view.")
        for i in items:
            getattr(self.view, control).insert_item(False, *i)

    def install(self, *args, **kwargs):
        super(blacklistInteractor, self).install(*args, **kwargs)
        widgetUtils.connect_event(self.view.unblock, widgetUtils.BUTTON_PRESSED, self.on_unblock)
        pub.subscribe(self.add_items, self.modulename+"_add_items")

    def uninstall(self):
        super(blacklistInteractor, self).uninstall()
        pub.unsubscribe(self.add_items, self.modulename+"_add_items")


    def on_unblock(self, *args, **kwargs):
        question = commonMessages.unblock_person()
        if question == widgetUtils.NO:
            return
        item = self.view.persons.get_selected()
        if self.presenter.unblock_person(item) == 1:
            self.view.persons.remove_item(item)
