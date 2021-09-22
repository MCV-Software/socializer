from __future__ import unicode_literals
import unittest
from . import testconfig
import languageHandler
from sessionmanager import utils
from sessionmanager import renderers

class renderersTestCase(unittest.TestCase):

    def setUp(self):
        languageHandler.setLanguage("en")
        vk = testconfig.get_vk()
        self.vk = vk.get_api()

    def test_render_person(self):
        """ Test the person renderer function."""
        user = self.vk.users.get(user_ids=1, fields="first_name, last_name, last_seen")
        self.assertIsInstance(user, list)
        self.assertEquals(len(user), 1)
        user = user[0]
        rendered_object = renderers.render_person(user, user["last_seen"])
        self.assertIsInstance(rendered_object, list)
        self.assertEquals(len(rendered_object), 2)
        self.assertIsInstance(rendered_object[0], str)
        self.assertIsInstance(rendered_object[1], str)

if __name__ == "__main__":
    unittest.main()
