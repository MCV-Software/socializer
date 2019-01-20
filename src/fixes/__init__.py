# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from . import fix_requests

#if hasattr(sys, "frozen"):
from . import fix_win32com
from . import fix_libloader

def setup():
	fix_requests.fix()
#	if hasattr(sys, "frozen"):
	fix_libloader.fix()
	fix_win32com.fix()