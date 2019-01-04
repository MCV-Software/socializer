# -*- coding: utf-8 -*-
import unittest
import mock
import languageHandler
from presenters import audioRecorder as presenter
from interactors import audioRecorder as interactor

class audioRecorderTestCase(unittest.TestCase):

	""" Test both the presenter and interactor of the audio recorder feature. View stuff will be mocked."""

#	@mock.patch("presenters.audioRecorder.sound_lib", esp_set=True)
#	@mock.patch("presenters.audioRecorder.pub", esp_set=True)
#	@mock.patch("presenters.audioRecorder.tempfile", esp_set=True)
#	@mock.patch("presenters.audioRecorder.sound", esp_set=True)
#	@mock.patch("presenters.audioRecorder.output", esp_set=True)
#	@mock.patch("presenters.audioRecorder.os", esp_set=True)
#	def test_audiorecorder_interactor(self, soundlib_mock, pub_mock, tempfile_mock, sound_mock, output_mock, os_mock, widgetUtils_mock, interactor_pub_mock):
#		""" Test methods for audio recorder. """
#		tempfile_mock.mktemp.return_value = "somefile.wav"
#		sound_mock.get_recording.return_value = "some_recording"
#		view=mock.MagicMock(name="view")
#		interactor_ = interactor.audioRecorderInteractor()
#		presenter_ = presenter.audioRecorderPresenter(view=view, interactor=interactor_)
#		interactor_.install.assert_called_with(view=view, presenter=presenter_)
#		interactor_.start.assert_called_with()
#		# Start sending events to the presenter and see its reactions.
#		presenter_.start_recording()
#		print(presenter_.recording)

	@mock.patch("interactors.base.pub", esp_set=True)
	@mock.patch("interactors.audioRecorder.widgetUtils", esp_set=True)
	def test_audiorecorder_interactor(self, widgetUtils_mock, pub_mock):
		pub_mock.subscribe.return_value = True
		view=mock.MagicMock(name="view")
		interactor_ = interactor.audioRecorderInteractor()
		presenter_ = mock.MagicMock(name="Presenter", esp_set=presenter.audioRecorderPresenter)
		interactor_.install(view=view, presenter=presenter_)
		print(pub_mock.subscribe.called)

	def setUp(self):
		languageHandler.setLanguage("en")

if __name__ == "__main__":
	unittest.main()