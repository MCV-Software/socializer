# -*- coding: utf-8 -*-
import unittest
import mock
from interactors import base

class baseInteractorTestCase(unittest.TestCase):
	""" some tests for the base interactor implementation."""

	@mock.patch("interactors.base.pub", esp_set=True)
	def test_base_interactor(self, pub_mock):
		""" Test the base interactor class. """
		view=mock.MagicMock(name="view")
		interactor_ = base.baseInteractor()
		presenter_ = mock.MagicMock(name="Presenter")
		interactor_.install(view=view, presenter=presenter_, modulename="base")
		# Check if the interactor has called pubsub correctly.
		pub_mock.subscribe.assert_any_call(interactor_.disable_control, "base_disable_control"),
		pub_mock.subscribe.assert_any_call(interactor_.enable_control, "base_enable_control"),
		pub_mock.subscribe.assert_any_call(interactor_.set_label, "base_set_label"),
		pub_mock.subscribe.assert_any_call(interactor_.focus_control, "base_focus_control")
		# Now, simulate some event calls.
		interactor_.disable_control(control="some_control")
		view.disable.assert_called_with("some_control")
		interactor_.enable_control(control="some_control")
		view.enable.assert_called_with("some_control")
		interactor_.focus_control(control="some_control")
		view.some_control.SetFocus()
		interactor_.uninstall()
		pub_mock.unsubscribe.assert_any_call(interactor_.disable_control, "base_disable_control"),
		pub_mock.unsubscribe.assert_any_call(interactor_.enable_control, "base_enable_control"),
		pub_mock.unsubscribe.assert_any_call(interactor_.set_label, "base_set_label"),
		pub_mock.unsubscribe.assert_any_call(interactor_.focus_control, "base_focus_control")

if __name__ == "__main__":
	unittest.main()