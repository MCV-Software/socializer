import sys
import unittest
import application

class py2exeTestCase(unittest.TestCase):

	@unittest.skipUnless(sys.version[0] == "2", "this only fails under Python 2")
	def test_application_not_unicode(self):
		""" Testing if some strings present in application have not changed to unicode. """
		self.assertIsInstance(application.name, str)
		self.assertIsInstance(application.author, str)
		self.assertIsInstance(application.authorEmail, str)
		self.assertIsInstance(application.version, str)
		self.assertIsInstance(application.url, str)

if __name__ == "__main__":
	unittest.main()