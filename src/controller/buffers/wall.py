# -*- coding: utf-8 -*-
""" A buffer is a (virtual) list of items. All items belong to a category (wall posts, messages, persons...)"""
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
from mysc.thread_utils import call_threaded
from wxUI import commonMessages
from .home import homeBuffer

log = logging.getLogger("controller.buffers.wall")

class wallBuffer(homeBuffer):
    """ This buffer represents an user's wall. It may be used either for the current user or someone else."""

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

    def remove_buffer(self, mandatory=False):
        """ Remove buffer if the current buffer is not the logged user's wall."""
        if "me_feed" == self.name:
            output.speak(_("This buffer can't be deleted"))
            return False
        else:
            if mandatory == False:
                dlg = commonMessages.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                self.session.db.pop(self.name)
                return True
            else:
                return False

    def __init__(self, *args, **kwargs):
        super(wallBuffer, self).__init__(*args, **kwargs)
        self.user_key = "from_id"
        self.post_key = "id"
        self.can_post = True
        self.can_write_private_message = True
        # if this is an user timeline we must check permissions to hide buttons when needed.
        if "owner_id" in self.kwargs and self.kwargs["owner_id"] > 0 and "feed" in self.name:
            permissions = self.session.vk.client.users.get(user_ids=self.kwargs["owner_id"], fields="can_post, can_see_all_posts, can_write_private_message")
            self.can_post = permissions[0]["can_post"]
            self.can_see_all_posts = permissions[0]["can_see_all_posts"]
            self.can_write_private_message = permissions[0]["can_write_private_message"]
            log.debug("Checked permissions on buffer {0}, permissions were {1}".format(self.name, permissions))

    def post(self, *args, **kwargs):
        """ Create a post in the wall for the specified user
        This process is handled in two parts. This is the first part, where the GUI is created and user can send the post.
        During the second part (threaded), the post will be sent to the API."""
        if "owner_id" not in self.kwargs:
            return super(wallBuffer, self).post()
        owner_id = self.kwargs["owner_id"]
        user = self.session.get_user(owner_id, key="user1")
        title = _("Post to {user1_nom}'s wall").format(**user)
        p = presenters.createPostPresenter(session=self.session, interactor=interactors.createPostInteractor(), view=views.createPostDialog(title=title, message="", text=""))
        if hasattr(p, "text") or hasattr(p, "privacy"):
            post_arguments=dict(privacy=p.privacy, message=p.text, owner_id=owner_id)
            attachments = []
            if hasattr(p, "attachments"):
                attachments = p.attachments
            call_threaded(pub.sendMessage, "post", parent_endpoint="wall", child_endpoint="post", from_buffer=self.name, attachments_list=attachments, post_arguments=post_arguments)

    def open_in_browser(self, *args, **kwargs):
        post = self.get_post()
        if post == None:
            return
        url = "https://vk.com/wall{user_id}_{post_id}".format(user_id=post["from_id"], post_id=post["id"])
        webbrowser.open_new_tab(url)
