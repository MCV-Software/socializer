# -*- coding: utf-8 -*-
import unittest
import mock
import languageHandler
from presenters import audioRecorder as presenter
from interactors import audioRecorder as interactor

class audioRecorderTestCase(unittest.TestCase):

	""" Test both the presenter and interactor of the audio recorder feature. View stuff will be mocked."""

	@mock.patch("presenters.audioRecorder.sound_lib", esp_set=True)
	@mock.patch("presenters.base.pub", esp_set=True)
	@mock.patch("presenters.audioRecorder.tempfile", esp_set=True)
	@mock.patch("presenters.audioRecorder.sound", esp_set=True)
	@mock.patch("presenters.audioRecorder.output", esp_set=True)
	@mock.patch("presenters.audioRecorder.os", esp_set=True)
	def test_audiorecorder_presenter(self, os_mock, output_mock, sound_mock, tempfile_mock, pub_mock, soundlib_mock):
		""" Test methods for audio recorder presenter. """
		tempfile_mock.mktemp.return_value = "somefile.wav"
		sound_mock.get_recording.return_value = mock.MagicMock()
		soundlib_mock.stream.fileStream.return_value = mock.MagicMock()
		view=mock.MagicMock(name="view")
		interactor_ = mock.MagicMock(name="interactor", esp_set=interactor.audioRecorderInteractor)
		presenter_ = presenter.audioRecorderPresenter(view=view, interactor=interactor_)
		# Start sending events to the presenter and see its reactions.
		presenter_.start_recording()
		tempfile_mock.mktemp.assert_any_call(suffix=".wav")
		sound_mock.get_recording.assert_any_call(presenter_.file)
		presenter_.recording.play.assert_any_call()
		pub_mock.sendMessage.assert_any_call("audiorecorder_set_label", control="record", label=_("&Stop"))
		pub_mock.sendMessage.assert_any_call("audiorecorder_disable_control", control="ok")
		presenter_.stop_recording()
		presenter_.recording.stop.assert_any_call()
		presenter_.recording.free.assert_any_call()
		pub_mock.sendMessage.assert_any_call("audiorecorder_set_label", control="record", label=_("&Record"))
		pub_mock.sendMessage.assert_any_call("audiorecorder_disable_control", control="record")
		pub_mock.sendMessage.assert_any_call("audiorecorder_enable_control", control="play")
		pub_mock.sendMessage.assert_any_call("audiorecorder_enable_control", control="discard")
		pub_mock.sendMessage.assert_any_call("audiorecorder_enable_control", control="ok")
		pub_mock.sendMessage.assert_any_call("audiorecorder_focus_control", control="play")
		presenter_.discard_recording()
		self.assertTrue(presenter_.playing==None)

	@mock.patch("interactors.audioRecorder.widgetUtils", esp_set=True)
	def test_audiorecorder_interactor(self, widgetUtils_mock):
		view=mock.MagicMock(name="view")
		interactor_ = interactor.audioRecorderInteractor()
		presenter_ = mock.MagicMock(name="Presenter", esp_set=presenter.audioRecorderPresenter)
		interactor_.install(view=view, presenter=presenter_)
		# Test if events have been connected to WX
		widgetUtils_mock.connect_event.assert_any_call(view.play, widgetUtils_mock.BUTTON_PRESSED, interactor_.on_play)
		widgetUtils_mock.connect_event.assert_any_call(view.record, widgetUtils_mock.BUTTON_PRESSED, interactor_.on_record)
		widgetUtils_mock.connect_event.assert_any_call(view.discard, widgetUtils_mock.BUTTON_PRESSED, interactor_.on_discard)
		# Let's call some methods simulating user interaction.
		interactor_.on_record()
		presenter_.toggle_recording.assert_called_with()
		interactor_.on_play()
		presenter_.play.assert_called_with()
		# Let's simulate user response here
		view.get_response.return_value = widgetUtils_mock.OK
		interactor_.start()
		# this should call on_postprocess after receiving the OK signal.
		presenter_.postprocess.assert_called_with()

	def setUp(self):
		languageHandler.setLanguage("en")

if __name__ == "__main__":
	unittest.main()