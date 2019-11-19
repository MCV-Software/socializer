# -*- coding: utf-8 -*-
""" A "presenter" in the socializer's terminology is a module that handles business logic in the application's workflow.
	All presenter classes should derive from base.basePresenter and will be completely abstracted from views (the GUI elements). It means presenters and views don't know anything about the each other.
	Both Presenters and views can communicate through the interactors. Interactors are responsible to receive user input and send requests to the presenters, aswell as receiving presenter requests and render those in the view.
	So, in a tipical user interaction made in socializer, the following could happen when someone decides to do something:
	1. A new presenter is  created, with two mandatory arguments: The corresponding view and interactor.
	2. The presenter will call to the install() method in the interactor, to connect all GUI events to their corresponding methods. All of these functions will be present in the interactor only.
	3. After install(), the presenter will run the View, which will display the graphical user interface that users can see and interact with. The view is the only layer directly accessible from the user world and does not handle any kind of logic.
	4. If the user presses a button or generates an event connected to a function in the interactor side, the function will be executed in the interactor. The interactor is aware of the View, and holds a reference to the presenter. The interactor should call other GUI elements if necessary and handle some logic (related to GUI, like yes/no dialogs). The interactor can call the presenter to retrieve some information, though the interactor cannot perform any business logic (like altering the cache database, retrieving usernames and so on).
	5. If the interactor calls something in the presenter, it will be executed. The presenter knows everything about VK and the session object, so it will fetch data, save it in the cache, call other methods from VK and what not. If the presenter wants to change something in the GUI elements (for example, hiding a control or displaying something else), it will send a pubsub event that the interactor will receive and act on accordingly.
	
	By using this design pattern it allows more decoupled code, easier testing (as we don't need to instantiate the views) and easy to switch (or add) a new graphical user interface by replacing interactors and views.
"""
from . import player
from .base import *
from .attach import *
from .audioRecorder import *
from .blacklist import *
from .createPosts import *
from .displayPosts import *
from .configuration import *
from .profiles import *