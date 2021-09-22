# -*- coding: utf-8 -*-
import webbrowser
import logging
from pubsub import pub
from presenters import base

log = logging.getLogger(__file__)

class displayFriendshipPresenter(base.basePresenter):

    def __init__(self, session, postObject, view, interactor, caption=""):
        self.session = session
        self.post = postObject
        super(displayFriendshipPresenter, self).__init__(view=view, interactor=interactor, modulename="display_friendship")
        list_of_friends = self.get_friend_names()
        from_ = self.session.get_user(self.post["source_id"])
        title = caption.format(**from_)
        self.send_message("set_title", value=title)
        self.set_friends_list(list_of_friends)
        self.run()

    def get_friend_names(self):
        self.friends = self.post["friends"]["items"]
        friends = list()
        for i in self.friends:
            if "user_id" in i:
                friends.append(self.session.get_user(i["user_id"])["user1_nom"])
            else:
                friends.append(self.session.get_user(i["id"])["user1_nom"])
        return friends

    def set_friends_list(self, friendslist):
        self.send_message("add_items", control="friends", items=friendslist)

    def view_profile(self, item):
        user = self.friends[item]
        if "user_id" in user:
            id = user["user_id"]
        else:
            id = user["id"]
        pub.sendMessage("user-profile", person=id)

    def open_in_browser(self, item):
        user = self.friends[item]
        if "user_id" in user:
            id = user["user_id"]
        else:
            id = user["id"]
        url = "https://vk.com/id{user_id}".format(user_id=id)
        webbrowser.open_new_tab(url)
