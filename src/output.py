# *- coding: utf-8 -*-
import logging as original_logging
logging = original_logging.getLogger('core.output')

from accessible_output2 import outputs
import sys

speaker = None

def speak(text, interrupt=0):
	global speaker
	if not speaker:
		setup()
	speaker.speak(text, interrupt)
	speaker.braille(text)

def setup ():
	global speaker
	logging.debug("Initializing output subsystem.")
	try:
		speaker = outputs.auto.Auto()
	except:
		return logging.exception("Output: Error during initialization.")

