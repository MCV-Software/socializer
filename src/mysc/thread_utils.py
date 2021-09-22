# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
import threading

def call_threaded(func, *args, **kwargs):
    #Call the given function in a daemonized thread and return the thread.
    def new_func(*a, **k):
#  try:
        func(*a, **k)
#  except:
#   pass
    thread = threading.Thread(target=new_func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread
