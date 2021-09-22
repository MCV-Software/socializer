# -*- coding: utf-8 -*-
import logging
import webbrowser
import arrow
import wx
import presenters
import views
import interactors
import languageHandler
import widgetUtils
import output
from pubsub import pub
from vk_api.exceptions import VkApiError
from presenters import player
from wxUI.tabs import home
from sessionmanager import session, renderers
from mysc.thread_utils import call_threaded
from wxUI import commonMessages, menus

log = logging.getLogger("controller.buffers.home")

class homeBuffer(object):
    """ a basic representation of a buffer. Other buffers should be derived from this class. This buffer represents the "news feed" """

    def get_post(self):
        """ Return the currently focused post."""
        # Handle case where there are no items in the buffer.
        if self.tab.list.get_count() == 0:
            wx.Bell()
            return None
        return self.session.db[self.name]["items"][self.tab.list.get_selected()]

    def __init__(self, parent=None, name="", session=None, composefunc=None, create_tab=True, *args, **kwargs):
        """ Constructor:
        @parent wx.Treebook: parent for the buffer panel,
        @name str: Name for saving this buffer's data in the local storage variable,
        @session sessionmanager.session.vkSession: Session for performing operations in the Vk API. This session should be logged in when this class is instanciated.
        @composefunc str: This function will be called for composing the result which will be put in the listCtrl. Composefunc should exist in the sessionmanager.renderers module.
        args and kwargs will be passed to get_items() without any filtering. Be careful there.
        """
        super(homeBuffer, self).__init__()
        self.parent = parent
        self.args = args
        self.kwargs = kwargs
        self.session = session
        self.compose_function = composefunc
        self.name = name
        if create_tab:
            self.create_tab(self.parent)
     #Update_function will be called every 3 minutes and it should be able to
        # Get all new items in the buffer and sort them properly in the CtrlList.
        # ToDo: Shall we allow dinamically set for update_function?
        self.update_function = "get_page"
        self.name = name
        # source_key and post_key will point to the keys for sender and posts in VK API objects.
        # They can be changed in the future for other item types in different buffers.
        self.user_key = "source_id"
        self.post_key = "post_id"
        # When set to False, update_function won't be executed here.
        self.can_get_items = True

    def create_tab(self, parent):
        """ Create the Wx panel."""
        self.tab = home.homeTab(parent)
        # Bind local events (they will respond to events happened in the buffer).
        self.connect_events()
        self.tab.name = self.name
        if hasattr(self, "can_post") and self.can_post == False and hasattr(self.tab, "post"):
            self.tab.post.Enable(False)

    def insert(self, item, reversed=False):
        """ Add a new item to the list. Uses renderers.composefunc for parsing the dictionary and create a valid result for putting it in the list."""
        try:
            item_ = getattr(renderers, self.compose_function)(item, self.session)
            wx.CallAfter(self.tab.list.insert_item, reversed, *item_)
        except:
            log.exception(item)

    def get_items(self, show_nextpage=False):
        """ Retrieve items from the VK API. This function is called repeatedly by the main controller and users could call it implicitly as well with the update buffer option.
        @show_nextpage boolean: If it's true, it will try to load previous results.
        """
        if self.can_get_items == False: return
        retrieved = True # Control variable for handling unauthorised/connection errors.
        try:
            num = getattr(self.session, "get_newsfeed")(show_nextpage=show_nextpage, name=self.name, *self.args, **self.kwargs)
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
        if show_nextpage  == False:
            if self.tab.list.get_count() > 0 and num > 0:
                v = [i for i in self.session.db[self.name]["items"][:num]]
                v.reverse()
                [wx.CallAfter(self.insert, i, True) for i in v]
            else:
                [wx.CallAfter(self.insert, i) for i in self.session.db[self.name]["items"][:num]]
        else:
            if num > 0:
                [wx.CallAfter(self.insert, i, False) for i in self.session.db[self.name]["items"][-num:]]
        return retrieved

    def get_more_items(self):
        """ Returns previous items in the buffer."""
        self.get_items(show_nextpage=True)

    def post(self, *args, **kwargs):
        """ Create a post in the current user's wall.
        This process is handled in two parts. This is the first part, where the GUI is created and user can send the post.
        During the second part (threaded), the post will be sent to the API."""
        p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Write your post"), message="", text=""))
        if hasattr(p, "text") or hasattr(p, "privacy"):
            post_arguments=dict(privacy=p.privacy, message=p.text)
            attachments = []
            if hasattr(p, "attachments"):
                attachments = p.attachments
            call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="post", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)

    def connect_events(self):
        """ Bind all events to this buffer"""
        widgetUtils.connect_event(self.tab.post, widgetUtils.BUTTON_PRESSED, self.post)
        widgetUtils.connect_event(self.tab.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.tab.list.list, wx.EVT_CONTEXT_MENU, self.show_menu)
        self.tab.set_focus_function(self.onFocus)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        """ Show contextual menu when pressing menu key or right mouse click in a list item."""
        if self.tab.list.get_count() == 0: return
        menu = self.get_menu()
        if pos != 0:
            self.tab.PopupMenu(menu, pos)
        else:
            self.tab.PopupMenu(menu, self.tab.list.list.GetPosition())

    def show_menu_by_key(self, ev):
        """ Show contextual menu when menu key is pressed"""
        if self.tab.list.get_count() == 0:
            return
        if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
            self.show_menu(widgetUtils.MENU, pos=self.tab.list.list.GetPosition())

    def get_menu(self):
        """ Returns contextual menu options. They will change according to the focused item"""
        p = self.get_post()
        if p == None:
            return
        # determine if the current user is able to delete the object.
        if "can_delete" in p:
            can_delete = True==p["can_delete"]
        else:
            can_delete = False
        m = menus.postMenu(can_delete=can_delete)
        if ("likes" in p) == False:
            m.like.Enable(False)
        elif p["likes"]["user_likes"] == 1:
            m.like.Enable(False)
            m.dislike.Enable(True)
        if ("comments" in p) == False:
            m.comment.Enable(False)
        m.open_in_browser.Enable(False)
        if "type" in p and p["type"] != "friend" and p["type"] != "audio" and p["type"] != "video" and p["type"] != "playlist" or self.name != "home_timeline":
            m.open_in_browser.Enable(True)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_post, menuitem=m.open)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.do_like, menuitem=m.like)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.do_dislike, menuitem=m.dislike)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.do_comment, menuitem=m.comment)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.open_in_browser, menuitem=m.open_in_browser)
        if hasattr(m, "view_profile"):
            widgetUtils.connect_event(m, widgetUtils.MENU, self.open_person_profile, menuitem=m.view_profile)
        if hasattr(m, "delete"):
            widgetUtils.connect_event(m, widgetUtils.MENU, self.delete, menuitem=m.delete)
        return m

    def do_like(self, *args, **kwargs):
        """ Set like in the currently focused post."""
        post = self.get_post()
        if post == None:
            return
        user = post[self.user_key]
        id = post[self.post_key]
        if "type" in post:
            type_ = post["type"]
        else:
            type_ = "post"
        l = self.session.vk.client.likes.add(owner_id=user, item_id=id, type=type_)
        self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
        self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 1
        # Translators: This will be used when user presses like.
        output.speak(_("You liked this"))

    def do_dislike(self, *args, **kwargs):
        """ Set dislike (undo like) in the currently focused post."""
        post = self.get_post()
        if post == None:
            return
        user = post[self.user_key]
        id = post[self.post_key]
        if "type" in post:
            type_ = post["type"]
        else:
            type_ = "post"
        l = self.session.vk.client.likes.delete(owner_id=user, item_id=id, type=type_)
        self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["count"] = l["likes"]
        self.session.db[self.name]["items"][self.tab.list.get_selected()]["likes"]["user_likes"] = 2
        # Translators: This will be user in 'dislike'
        output.speak(_("You don't like this"))

    def do_comment(self, *args, **kwargs):
        """ Make a comment into the currently focused post."""
        post = self.get_post()
        if post == None:
            return
        comment = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=_("Add a comment"), message="", text="", mode="comment"))
        if hasattr(comment, "text") or hasattr(comment, "privacy"):
            msg = comment.text
            try:
                user = post[self.user_key]
                id = post[self.post_key]
                self.session.vk.client.wall.addComment(owner_id=user, post_id=id, text=msg)
                output.speak(_("You've posted a comment"))
            except Exception as msg:
                log.error(msg)

    def delete(self, *args, **kwargs):
        post = self.get_post()
        if ("type" in post and post["type"] == "post") or self.name != "newsfeed":
            question = commonMessages.remove_post()
            if question == widgetUtils.NO:
                return
            if "owner_id" in self.kwargs:
                result = self.session.vk.client.wall.delete(owner_id=self.kwargs["owner_id"], post_id=post[self.post_key])
            else:
                result = self.session.vk.client.wall.delete(post_id=post[self.post_key])
            pub.sendMessage("post_deleted", post_id=post[self.post_key])
            self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
            self.tab.list.remove_item(self.tab.list.get_selected())

    def get_event(self, ev):
        """ Parses keyboard input in the ListCtrl and executes the event associated with user keypresses."""
        if ev.GetKeyCode() == wx.WXK_RETURN: event = "open_post"
        else:
            event = None
            ev.Skip()
        if event != None:
            try:
                getattr(self, event)()
            except AttributeError:
                pass

    def volume_down(self):
        """ Decreases player volume by 2%"""
        player.player.volume = player.player.volume-2

    def volume_up(self):
        """ Increases player volume by 2%"""
        player.player.volume = player.player.volume+2

    def play_audio(self, *args, **kwargs):
        """ Play audio in currently focused buffer, if possible."""
        post = self.get_post()
        if post == None:
            return
        if "type" in post and post["type"] == "audio":
            pub.sendMessage("play", object=post["audio"]["items"][0])
            return True

    def open_person_profile(self, *args, **kwargs):
        """ Views someone's profile."""
        selected = self.get_post()
        if selected == None:
            return
        # Check all possible keys for an user object in VK API.
        keys = ["from_id", "source_id", "id"]
        for i in keys:
            if i in selected:
                pub.sendMessage("user-profile", person=selected[i])
                break

    def open_post(self, *args, **kwargs):
        """ Opens the currently focused post."""
        post = self.get_post()
        if post == None:
            return
        if "type" in post and post["type"] == "audio":
            a = presenters.displayAudioPresenter(session=self.session, postObject=post["audio"]["items"], interactor=interactors.displayAudioInteractor(), view=views.displayAudio())
        elif "type" in post and post["type"] == "friend":
            pub.sendMessage("open-post", post_object=post, controller_="displayFriendship", vars=dict(caption=_("{user1_nom} added the following friends")))
        else:
            pub.sendMessage("open-post", post_object=post, controller_="displayPost")

    def pause_audio(self, *args, **kwargs):
        """ pauses audio playback."""
        pub.sendMessage("pause")

    def remove_buffer(self, mandatory):
        """ Function for removing a buffer. Returns True if removal is successful, False otherwise"""
        return False

    def get_users(self):
        """ Returns source user in the post."""
        post = self.get_post()
        if post == None:
            return
        if ("type" in post) == False:
            return [post["from_id"]]
        else:
            return [post["source_id"]]

    def onFocus(self, event, *args,**kwargs):
        """ Function executed when the item in a list is selected.
        For this buffer it updates the date of posts in the list."""
        post = self.get_post()
        if post == None:
            return
        original_date = arrow.get(post["date"])
        created_at = original_date.humanize(locale=languageHandler.curLang[:2])
        self.tab.list.list.SetItem(self.tab.list.get_selected(), 2, created_at)
        event.Skip()

    def open_in_browser(self, *args, **kwargs):
        post = self.get_post()
        if post == None:
            return
        url = "https://vk.com/wall{user_id}_{post_id}".format(user_id=post["source_id"], post_id=post["post_id"])
        webbrowser.open_new_tab(url)
