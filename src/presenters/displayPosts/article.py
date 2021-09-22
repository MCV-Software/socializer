# -*- coding: utf-8 -*-
""" Presenter to render an article from the VK mobile website.
this is an helper class to display an article within socializer, as opposed to opening a web browser and asking the user to get there.
"""
import logging
import re
from bs4 import BeautifulSoup
from presenters import base

log = logging.getLogger(__file__)

class displayArticlePresenter(base.basePresenter):
    def __init__(self, session, postObject, view, interactor):
        super(displayArticlePresenter, self).__init__(view=view, interactor=interactor, modulename="display_article")
        self.session = session
        self.post = postObject
        self.load_article()
        self.run()

    def load_article(self):
        """ Loads the article in the interactor.
        This function retrieves, by using the params defined in the VK API, the web version of the article and extracts some info from it.
        this is needed because there are no public API for articles so far.
        """
        article = self.post[0]
        # By using the vk_api's session, proxy settings are applied, thus might work in blocked countries.
        article_body = self.session.vk.session_object.http.get(article["view_url"])
        # Parse and extract text from all paragraphs.
        # ToDo: Extract all links and set those as attachments.
        soup = BeautifulSoup(article_body.text, "lxml")
        # ToDo: Article extraction require testing to see if you can add more tags beside paragraphs.
        msg = [p.get_text() for p in soup.find_all("p")]
        msg = "\n\n".join(msg)
        self.send_message("set", control="article_view", value=msg)
        self.send_message("set_title", value=article["title"])
        # Retrieve views count
        views = soup.find("div", class_="articleView__views_info")
        # This might return None if VK changes anything, so let's avoid errors.
        if views == None:
            views = str(-1)
        else:
            views = views.text
            # Find the integer and remove the words from the string.
            numbers = re.findall(r'\d+', views)
            if len(numbers) != 0:
                views = numbers[0]
        self.send_message("set", control="views", value=views)
