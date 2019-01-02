# -*- coding: utf-8 -*-
import platform
from . import translator
if platform.system() == "Windows":
 from . import wx_ui as gui
 