# socializer 

A desktop application for handling [vk.com](http://vk.com) in an easy way.

## Warning

This source code is completely experimental. The current functionality in this application is not very useful. If you are not a developer, or you don't know how to deal with Python code and some network Rest API'S, probably you should not clone this repository and run the application. If you decide to do so, take into account that this doesn't work as an application yet.

I have started this effort as an open source  project on Feb 13, 2016. Pull requests and bug reports are welcome. Socializer is not a definitive name for this project, it could be changed in future.

## dependencies

* [Python,](http://python.org) version 2.7.11
* [wxPython](http://www.wxpython.org) for Python 2.7, version 3.0.2.0
* [Python windows extensions (pywin32)](http://www.sourceforge.net/projects/pywin32/) for python 2.7, build 220
* [PyEnchant,](http://pythonhosted.org/pyenchant/) version 1.6.6.
* [VK API bindings for Python](https://github.com/dimka665/vk) (already included in the SRC directory)
* pypubsub
* configobj
* requests-oauthlib
* future
* arrow==0.6
* microsofttranslator

## Running

Just open the main.py file with the python interpreter. This file is located in the src directory. If you haven't configured your VK account, you'll have to press "new account" in the first dialogue, a new dialogue will  prompt for an user email and the password for your account. Even if the session manager, in theory, allows to configure more than one account, the application will initialize only the first detected account. Take into account that the provided information will be saved in a config file as plain text. This application will need your email and password for renegotiating the access token when it expires.

