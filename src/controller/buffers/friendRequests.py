# -*- coding: utf-8 -*-
import logging
import wx
from pubsub import pub
from vk_api.exceptions import VkApiError
from .people import peopleBuffer

log = logging.getLogger("controller.buffers.friendRequests")

class friendRequestsBuffer(peopleBuffer):

    def get_items(self, show_nextpage=False):
        if self.can_get_items == False: return
        retrieved = True
        try:
            ids = self.session.vk.client.friends.getRequests(*self.args, **self.kwargs)
        except VkApiError as err:
            log.error("Error {0}: {1}".format(err.code, err.error))
            retrieved = err.code
            return retrieved
        except:
            log.exception("Connection error when updating buffer %s. Will try again in 2 minutes" % (self.name,))
            return False
        num = self.session.get_page(name=self.name, show_nextpage=show_nextpage, endpoint="get", parent_endpoint="users", count=1000, user_ids=", ".join([str(i) for i in ids["items"]]), fields="uid, first_name, last_name, last_seen")
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
        return retrieved

    def accept_friendship(self, *args, **kwargs):
        """ Adds a person to a list of friends. This method is done for accepting someone else's friend request.
        https://vk.com/dev/friends.add
        """
        person = self.get_post()
        if person == None:
            return
        result = self.session.vk.client.friends.add(user_id=person["id"])
        if result == 2:
            msg = _("{0} {1} now is your friend.").format(person["first_name"], person["last_name"])
            pub.sendMessage("notify", message=msg)
            self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
            self.tab.list.remove_item(self.tab.list.get_selected())

    def decline_friendship(self, *args, **kwargs):
        """ Declines a freind request.
        https://vk.com/dev/friends.delete
        """
        person = self.get_post()
        if person == None:
            return
        result = self.session.vk.client.friends.delete(user_id=person["id"])
        if "out_request_deleted" in result:
            msg = _("You've deleted the friends request to {0} {1}.").format(person["first_name"], person["last_name"])
        elif "in_request_deleted" in result:
            msg = _("You've declined the friend request of {0} {1}.").format(person["first_name"], person["last_name"])
        pub.sendMessage("notify", message=msg)
        self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
        self.tab.list.remove_item(self.tab.list.get_selected())

    def keep_as_follower(self, *args, **kwargs):
        """ Adds a person to The followers list of the current user.
        https://vk.com/dev/friends.add
        """
        person = self.get_post()
        if person == None:
            return
        result = self.session.vk.client.friends.add(user_id=person["id"], follow=1)
        if result == 2:
            msg = _("{0} {1} is following you.").format(person["first_name"], person["last_name"])
            pub.sendMessage("notify", message=msg)
            self.session.db[self.name]["items"].pop(self.tab.list.get_selected())
            self.tab.list.remove_item(self.tab.list.get_selected())
