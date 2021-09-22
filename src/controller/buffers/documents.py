# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
import logging
import webbrowser
import arrow
import wx
import languageHandler
import widgetUtils
import output
from pubsub import pub
from wxUI.tabs import documents
from sessionmanager import utils
from mysc.thread_utils import call_threaded
from wxUI import menus
from .wall import wallBuffer

log = logging.getLogger("controller.buffers.documents")

class documentsBuffer(wallBuffer):
    can_get_items = False

    def create_tab(self, parent):
        self.tab = documents.documentsTab(parent)
        self.connect_events()
        self.tab.name = self.name
        if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
            self.tab.post.Enable(False)

    def onFocus(self, event, *args,**kwargs):
        post = self.get_post()
        if post == None:
            return
        original_date = arrow.get(post["date"])
        created_at = original_date.humanize(locale=languageHandler.curLang[:2])
        self.tab.list.list.SetItem(self.tab.list.get_selected(), 4, created_at)
        event.Skip()

    def connect_events(self):
        super(documentsBuffer, self).connect_events()
        # Check if we have a load button in the tab, because documents community  buffers don't include it.
        if hasattr(self.tab, "load"):
            widgetUtils.connect_event(self.tab.load, widgetUtils.BUTTON_PRESSED, self.load_documents)

    def load_documents(self, *args, **kwargs):
        output.speak(_("Loading documents..."))
        self.can_get_items = True
        self.tab.load.Enable(False)
        wx.CallAfter(self.get_items)

    def get_menu(self):
        p = self.get_post()
        if p == None:
            return
        if p["owner_id"] == self.session.user_id:
            added = True
        else:
            added = False
        m = menus.documentMenu(added)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.add_remove_document, menuitem=m.action)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.download, menuitem=m.download)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_in_browser, menuitem=m.open_in_browser)
        return m

    def add_remove_document(self, *args, **kwargs):
        p = self.get_post()
        if p == None:
            return
        if p["owner_id"] == self.session.user_id:
            result = self.session.vk.client.docs.delete(owner_id=p["owner_id"], doc_id=p["id"])
            if result == 1:
                output.speak(_("The document has been successfully deleted."))
                self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
                self.tab.list.remove_item(self.tab.list.get_selected())
        else:
            result = self.session.vk.client.docs.add(owner_id=p["owner_id"], doc_id=p["id"])
            output.speak(_("The document has been successfully added."))

    def download(self, *args, **kwargs):
        post = self.get_post()
        filename = utils.safe_filename(post["title"])
        # If document does not end in .extension we must fix it so the file dialog will save it properly later.
        if filename.endswith(post["ext"]) == False:
            filename = filename+ "."+post["ext"]
        filepath = self.tab.get_download_path(filename)
        if filepath != None:
            pub.sendMessage("download-file", url=post["url"], filename=filepath)

    def open_in_browser(self, *args, **kwargs):
        post = self.get_post()
        if post == None:
            return
        url = "https://vk.com/doc{user_id}_{post_id}".format(user_id=post["owner_id"], post_id=post["id"])
        webbrowser.open_new_tab(url)
