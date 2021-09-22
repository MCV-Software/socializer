# -*- coding: utf-8 -*-
import time
import random
import logging
import webbrowser
import wx
import presenters
import views
import interactors
import widgetUtils
import output
from pubsub import pub
from vk_api.exceptions import VkApiError
from extra import translator, SpellChecker
from wxUI.tabs import chat
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus
from sessionmanager import renderers
from .home import homeBuffer

log = logging.getLogger("controller.buffers.chat")

class chatBuffer(homeBuffer):

    def insert(self, item, reversed=False):
        """ Add a new item to the list. Uses session.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
        # as this tab is based in a text control, we have to overwrite the defaults.
        item_ = getattr(renderers, self.compose_function)(item, self.session)
        # the self.chat dictionary will have (first_line, last_line) as keys and message ID as a value for looking into it when needed.
        # Here we will get first and last line of a chat message appended to the history.
        values = self.tab.add_message(item_[0], reverse=reversed)
        self.chats[values] = item["id"]

    def get_focused_post(self):
        """ Gets chat message currently in focus"""
        # this function replaces self.get_post for this buffer, as we rely in a TextCtrl control for getting chats.
        # Instead of the traditional method to do the trick.
        # Get text position here.
        position = self.tab.history.PositionToXY(self.tab.history.GetInsertionPoint())
        id_ = None
        # The dictionary keys should be looked in reverse order as we are interested in the last result only.
        for i in reversed(list(self.chats.keys())):
            # Check if position[2] (line position) matches with something in self.chats
            # (All messages, except the last one, should be able to be matched here).
            # position[2]+1 is added because line may start with 0, while in wx.TextCtrl.GetNumberOfLines() it returns a value counting from 1.
            if position[2]+1 >= i[0]:
                id_ = self.chats[i]
                # If we find our chat message, let's skip the rest of the loop.
                break
        # Retrieve here the object based in id_
        if id_ != None:
            for i in self.session.db[self.name]["items"]:
                if i["id"] == id_:
                    return i
        return False

    get_post = get_focused_post

    def onFocus(self, event, *args, **kwargs):
        if event.GetKeyCode() == wx.WXK_UP or event.GetKeyCode() == wx.WXK_DOWN or event.GetKeyCode() == wx.WXK_START or event.GetKeyCode() == wx.WXK_PAGEUP or event.GetKeyCode() == wx.WXK_PAGEDOWN or event.GetKeyCode() == wx.WXK_END:
            msg = self.get_focused_post()
            if msg == False: # Handle the case where the last line of the control cannot be matched to anything.
                return
            # Mark unread conversations as read.
            if "read_state" in msg and msg["read_state"] == 0 and "out" in msg and msg["out"] == 0:
                self.session.soundplayer.play("message_unread.ogg")
                call_threaded(self.session.vk.client.messages.markAsRead, peer_id=self.kwargs["peer_id"])
                [i.update(read_state=1) for i in self.session.db[self.name]["items"]]
            if "attachments" in msg and len(msg["attachments"]) > 0:
                self.tab.attachments.list.Enable(True)
                self.attachments = list()
                self.tab.attachments.clear()
                self.parse_attachments(msg)
            else:
                self.tab.attachments.list.Enable(False)
                self.tab.attachments.clear()
        event.Skip()

    def create_tab(self, parent):
        self.tab = chat.chatTab(parent)
        self.attachments = list()
        self.connect_events()
        self.tab.name = self.name
        if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
            self.tab.post.Enable(False)

    def connect_events(self):
        widgetUtils.connect_event(self.tab.send, widgetUtils.BUTTON_PRESSED, self.send_chat_to_user)
        widgetUtils.connect_event(self.tab.attachment, widgetUtils.BUTTON_PRESSED, self.add_attachment)
        widgetUtils.connect_event(self.tab.text, widgetUtils.KEYPRESS, self.catch_enter)
        widgetUtils.connect_event(self.tab.actions, widgetUtils.BUTTON_PRESSED, self.actions)
        self.tab.set_focus_function(self.onFocus)

    def catch_enter(self, event, *args, **kwargs):
        shift=event.ShiftDown()
        if event.GetKeyCode() == wx.WXK_RETURN and shift == False:
            return self.send_chat_to_user()
        t = time.time()
        if event.GetUnicodeKey() != wx.WXK_NONE and t-self.last_keypress > 5:
            self.last_keypress = t
            call_threaded(self.session.vk.client.messages.setActivity, peer_id=self.kwargs["peer_id"], type="typing")
        event.Skip()

    def get_items(self, show_nextpage=False):
        """ Update buffer with newest items or get older items in the buffer."""
        if self.can_get_items == False: return
        retrieved = True
        try:
            num = getattr(self.session, "get_page")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
        except VkApiError as err:
            log.error("Error {0}: {1}".format(err.code, err.error))
            retrieved = err.code
            return retrieved
        except:
            log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
            return False
        if not hasattr(self, "tab"):
            # Create GUI associated to this buffer.
            self.create_tab(self.parent)
            # Add name to the new control so we could look for it when needed.
            self.tab.name = self.name
        if show_nextpage  == False:
            if self.tab.history.GetValue() != "" and num > 0:
                v = [i for i in self.session.db[self.name]["items"][:num]]
                [self.insert(i, False) for i in v]
            else:
                [self.insert(i) for i in self.session.db[self.name]["items"][:num]]
        else:
            if num > 0:
                # At this point we save more CPU and mathematical work if we just delete everything in the chat history and readd all messages.
                # Otherwise we'd have to insert new lines at the top and recalculate positions everywhere else.
                # Firstly, we'd have to save the current focused object so we will place the user in the right part of the text after loading everything again.
                focused_post = self.get_post()
                self.chats = dict()
                wx.CallAfter(self.tab.history.SetValue, "")
                v = [i for i in self.session.db[self.name]["items"]]
                [self.insert(i) for i in v]
                # Now it's time to set back the focus in the post.
                for i in self.chats.keys():
                    if self.chats[i] == focused_post["id"]:
                        line = i[0]
                        wx.CallAfter(self.tab.history.SetInsertionPoint, self.tab.history.XYToPosition(0, line))
                        output.speak(_("Items loaded"))
                        break
        if self.unread == True and num > 0:
            self.session.db[self.name]["items"][-1].update(read_state=0)
        return retrieved

    def get_more_items(self):
        output.speak(_("Getting more items..."))
        call_threaded(self.get_items, show_nextpage=True)

    def add_attachment(self, *args, **kwargs):
        a = presenters.attachPresenter(session=self.session, view=views.attachDialog(voice_messages=True), interactor=interactors.attachInteractor())
        if len(a.attachments) != 0:
            self.attachments_to_be_sent = a.attachments

    def send_chat_to_user(self, *args, **kwargs):
        text = self.tab.text.GetValue()
        if text == "" and not hasattr(self, "attachments_to_be_sent"):
            wx.Bell()
            return
        self.tab.text.SetValue("")
        post_arguments = dict(random_id = random.randint(0, 100000), peer_id=self.kwargs["peer_id"])
        if len(text) > 0:
            post_arguments.update(message=text)
        if hasattr(self, "attachments_to_be_sent") and len(self.attachments_to_be_sent) > 0:
            attachments = self.attachments_to_be_sent[::]
        else:
            attachments = []
        call_threaded(pub.sendMessage, "post", parent_endpoint="messages", child_endpoint="send", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)
        if hasattr(self, "attachments_to_be_sent"):
            del self.attachments_to_be_sent

    def __init__(self, unread=False, *args, **kwargs):
        super(chatBuffer, self).__init__(*args, **kwargs)
        self.unread = unread
        self.chats = dict()
        self.peer_typing = 0
        self.last_keypress = time.time()

    def parse_attachments(self, post):
        attachments = []

        if "attachments" in post:
            for i in post["attachments"]:
                # We don't need the photos_list attachment, so skip it.
                if i["type"] == "photos_list":
                    continue
                try:
                    rendered_object = renderers.add_attachment(i)
                except:
                    log.exception("Error parsing the following attachment on chat: %r" % (i,))
                attachments.append(rendered_object)
                self.attachments.append(i)
        self.tab.attachments.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_attachment)
        self.tab.insert_attachments(attachments)

    def open_attachment(self, *args, **kwargs):
        index = self.tab.attachments.get_selected()
        attachment = self.attachments[index]
        if attachment["type"] == "audio":
            a = presenters.displayAudioPresenter(session=self.session, postObject=[attachment["audio"]], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
        elif attachment["type"] == "audio_message":
            link = attachment["audio_message"]["link_mp3"]
            pub.sendMessage("play-message", message_url=link)
        elif attachment["type"] == "link":
            output.speak(_("Opening URL..."), True)
            webbrowser.open_new_tab(attachment["link"]["url"])
        elif attachment["type"] == "doc":
            output.speak(_("Opening document in web browser..."))
            webbrowser.open(attachment["doc"]["url"])
        elif attachment["type"] == "video":
            # it seems VK doesn't like to attach video links as normal URLS, so we'll have to
            # get the full video object and use its "player" key  which will open a webbrowser in their site with a player for the video.
            # see https://vk.com/dev/attachments_w and and https://vk.com/dev/video.get
            # However, the flash player  isn't good  for visually impaired people (when you press play you won't be able to close the window with alt+f4), so it could be good to use the HTML5 player.
            # For firefox,  see https://addons.mozilla.org/ru/firefox/addon/force-html5-video-player-at-vk/
            # May be I could use a dialogue here for inviting people to use this addon in firefox. It seems it isn't possible to use this html5 player from the player URL.
            object_id = "{0}_{1}".format(attachment["video"]["owner_id"], attachment["video"]["id"])
            video_object = self.session.vk.client.video.get(owner_id=attachment["video"]["owner_id"], videos=object_id)
            video_object = video_object["items"][0]
            output.speak(_("Opening video in web browser..."), True)
            webbrowser.open_new_tab(video_object["player"])
        elif attachment["type"] == "photo":
            output.speak(_("Opening photo in web browser..."), True)
            # Possible photo sizes for looking in the attachment information. Try to use the biggest photo available.
            possible_sizes = [1280, 604, 130, 75]
            url = ""
            for i in possible_sizes:
                if "photo_{0}".format(i,) in attachment["photo"]:
                    url = attachment["photo"]["photo_{0}".format(i,)]
                    break
            if url != "":
                webbrowser.open_new_tab(url)
        if attachment["type"] == "wall":
            pub.sendMessage("open-post", post_object=attachment["wall"], controller_="displayPost")
        else:
            log.debug("Unhandled attachment: %r" % (attachment,))

    def clear_reads(self):
        for i in self.session.db[self.name]["items"]:
            if "read_state" in i and i["read_state"] == 0:
                i["read_state"] = 1

    def remove_buffer(self, mandatory=False):
        """ Remove buffer if the current buffer is not the logged user's wall."""
        if mandatory == False:
            dlg = commonMessages.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            self.session.db.pop(self.name)
            return True
        else:
            return False

    def open_in_browser(self, *args, **kwargs):
        peer_id = self.kwargs["peer_id"]
        url = "https://vk.com/im?sel={peer_id}".format(peer_id=peer_id)
        webbrowser.open_new_tab(url)

    def actions(self, *args, **kwargs):
        menu = menus.toolsMenu()
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.translate_action, menuitem=menu.translate)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.spellcheck_action, menuitem=menu.spellcheck)
        self.tab.PopupMenu(menu, self.tab.actions.GetPosition())

    def translate(self, text):
        dlg = translator.gui.translateDialog()
        if dlg.get_response() == widgetUtils.OK:
            language_dict = translator.translator.available_languages()
            for k in language_dict:
                if language_dict[k] == dlg.dest_lang.GetStringSelection():
                    dst = k
            msg = translator.translator.translate(text, dst)
            dlg.Destroy()
            return msg

    def spellcheck(self, text):
        checker = SpellChecker.spellchecker.spellChecker(text)
        if hasattr(checker, "fixed_text"):
            final_text = checker.fixed_text
            return final_text

    def translate_action(self, *args, **kwargs):
        text = self.tab.text.GetValue()
        if text == "":
            wx.Bell()
            return
        translated = self.translate(text)
        if translated != None:
            self.tab.text.ChangeValue(translated)
        self.tab.text.SetFocus()

    def spellcheck_action(self, *args, **kwargs):
        text = self.tab.text.GetValue()
        fixed = self.spellcheck(text)
        if fixed != None:
            self.tab.text.ChangeValue(fixed)
        self.tab.text.SetFocus()

    def translate_message(self, *args, **kwargs):
        pass

    def spellcheck_message(self, *args, **kwargs):
        pass
