# -*- coding: utf-8 -*-
import platform
if platform.system() == "Windows":
 from . import wx_ui as gui
from . import translator