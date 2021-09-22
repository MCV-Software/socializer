# -*- coding: utf-8 -*-
import output
import logging
from presenters import base

log = logging.getLogger(__file__)

class displayPollPresenter(base.basePresenter):

    def __init__(self, session, poll, view, interactor, show_results=False):
        super(displayPollPresenter, self).__init__(view=view, interactor=interactor, modulename="display_poll")
        self.poll = poll["poll"]
        self.session = session
        self.get_poll()
        self.load_poll(show_results)
        self.run()

    def get_poll(self):
        # Retrieve the poll again so we will have a fresh and updated object.
        data = dict(owner_id=self.poll["owner_id"], is_board=int(self.poll["is_board"]), poll_id=self.poll["id"])
        self.poll = self.session.vk.client.polls.getById(**data)

    def load_poll(self, load_results=False):
        user = self.session.get_user(self.poll["author_id"])
        title = _("Poll from {user1_nom}").format(**user)
        self.send_message("set_title", value=title)
        self.send_message("set", control="question", value=self.poll["question"])
        if len(self.poll["answer_ids"]) > 0 or ("is_closed" in self.poll and self.poll["is_closed"] == True) or load_results == True or ("can_vote" in self.poll and self.poll["can_vote"] == False):
            options = []
            for i in self.poll["answers"]:
                options.append((i["text"], i["votes"], i["rate"]))
            self.send_message("add_options", options=options, multiple=self.poll["multiple"])
            self.send_message("done")
            self.send_message("disable_control", control="ok")
        else:
            options = []
            for i in self.poll["answers"]:
                options.append(i["text"])
            self.send_message("add_options", options=options, multiple=self.poll["multiple"])
            self.send_message("done")

    def vote(self, answers):
        ids = ""
        for i in range(0, len(self.poll["answers"])):
            if answers[i] == True:
                ids = ids+"{answer_id},".format(answer_id=self.poll["answers"][i]["id"])
                if self.poll["multiple"] == False:
                    break
        if ids == "":
            log.exception("An error occurred when retrieving answer IDS for the following poll: %r. Provided answer list: %r" % (self.poll, answers))
            return
        data = dict(owner_id=self.poll["owner_id"], poll_id=self.poll["id"], answer_ids=ids, is_board=int(self.poll["is_board"]))
        result = self.session.vk.client.polls.addVote(**data)
        if result == 1:
            output.speak(_("Your vote has been added to this poll."))
