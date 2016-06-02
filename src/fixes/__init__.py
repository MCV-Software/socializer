# -*- coding: utf-8 -*-
import sys
import fix_requests
import fix_win32com

def setup():
	fix_requests.fix()
	if hasattr(sys, "frozen"):
		fix_win32com.fix()
