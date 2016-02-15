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

## Main interface

If you have used [TWBlue](https://github.com/manuelcortez/twblue) before, the socializer's interface is quite similar. Once you have authorised your account, you will see a window with the following elements:

* A tree view at the left of the window, where you will see the list of buffers (at the moment, there are only three of these: news feed, my wall and my audios).
* A button for making a post to your wall.
* A list where you will see the posts for the currently selected buffer.
* A status bar where the program will put some useful information about what it's doing at the moment.
* And a menu bar, that is not used yet.

When socializer starts, it will try to load your news items, wall and audios. At the moment there are only supported actions for the audio's buffer. You can play the currently selected song, view the song's details (including lyrics, if available) and download it to a desired place in your hard drive. There are no supported actions for posts yet.

### Making a post

When you press the post button, a new dialogue will show up. This dialogue allows you to post something in your wall. In this dialogue you have to write a message. You can translate your message and fix your spelling mistakes. Also you can post an URL address, socializer will try to add it as an attachment, so you will not have to worry about this. When you're ready, just press the send button and it'll done.

### Working with songs

If you want to play or view your audio's details, you'll have to navigate to the tree view, and, using the down arrow, look for "my audios". You will see two more buttons, play and play all. The play button will play the currently selected audio, and the play all button is not implemented yet. You can go to the song's list, look for a desired song and press the play button, or Ctrl+return, which is a keyboard shorcut.

When an  audio file is playing, you can press f5 and f6 for decreasing and increasing volume, respectively.

If you want to see  some details for the selected audio file, you can do it by pressing the return key. You will be able to read some useful information  (title, artist, duration and the lyric, if available). Also you will be able to download the song to your hard drive, you have to press the download button in the details' dialogue.

When the download starts, you can close the details dialogue and check the status bar in the main window for seeing the current progress.

