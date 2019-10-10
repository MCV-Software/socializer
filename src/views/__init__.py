""" Views package for socializer. A view is the Graphical user interface in the application. This package includes everything needed to render a window.
	No other functionality is assumed in this package.
	All modules from here should be used via an interactor (read description of the interactors package).
	Interactors will be routing user events (like buttons pressed, menus activated and so on) to presenter functions.
"""
from .dialogs.attach import *
from .dialogs.audioRecorder import *
from .dialogs.blacklist import *
from .dialogs.postCreation import *
from .dialogs.postDisplay import *
from .dialogs.configuration import *
from .dialogs.profiles import *