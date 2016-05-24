# socializer 

A desktop application for handling [vk.com](http://vk.com) in an easy way.

## weekly builds

Socializer's functionality is far to be perfect, in fact there are lots of methods of the VK API that this application doesn't support  right now, but if you are curious enough, and you want to help by giving me your impressions and making  tests for fixing  bugs, you can download the last source code, compiled as an application. This is the  weekly  build of socializer. This version is only for testing purposes, never think that it can be used for everyday use. This version does not include any documentation, Only the changelog, because it's build with an authomatic process. This weekly  build is built every week, depending in the updates that the repository has receibed.

Before downloading, take in to account the following: This source code is completely experimental. The current functionality in this application is not very useful. If you decide to use nightly build versions, take into account that this doesn't work as an application for everyday use yet.

Version: 2016.04.5  
Build date: Appril 5 2016  
[Download socializer weekly  build](https://github.com/manuelcortez/socializer/blob/master/nightly/socializer-nightly-build.zip?raw=true)

I have started this effort as an open source  project on Feb 13, 2016. Pull requests and bug reports are welcome. Socializer is not a definitive name for this project, it could be changed in future.

## dependencies

* [Python,](http://python.org) version 2.7.11
* [wxPython](http://www.wxpython.org) for Python 2.7, version 3.0.2.0
* [Python windows extensions (pywin32)](http://www.sourceforge.net/projects/pywin32/) for python 2.7, build 220
* [PyEnchant,](http://pythonhosted.org/pyenchant/) version 1.6.6.
* [VK API bindings for Python](https://github.com/dimka665/vk) (already included in the SRC directory)
* If you want to build your own versions, [Pandoc](http://pandoc.org/installing.html) make sure you have pandoc.exe in your path variable. If not, edit scripts/build.sh.
* pypubsub
* configobj
* requests-oauthlib
* future
* arrow==0.6
* microsofttranslator

## Running

Just open the main.py file with the python interpreter. This file is located in the src directory. If you haven't configured your VK account, you will see a dialogue, just press yes and a new dialogue will  prompt for an user email or phone number and the password for your account.  Take into account that the provided information will be saved in a config file as plain text. This application will need your information  for renegotiating the access token when it expires.

Note: Every time you grant access to socializer, probably You will receive an email from VK by telling you that someone has accessed to your account. It means that a new token has been negotiated between VK and socializer by using an authomatic process, you should ignore  those advices, unless you receive an email when you are not logged in VK with socializer or other application. You can see your authorised  applications in the configuration section in the VK website. New tokens are renegotiated every 24 hours.

## Main interface

If you have used [TWBlue](https://github.com/manuelcortez/twblue) before, the socializer's interface is quite similar. Once you have authorised your account, you will see a window with the following elements:

* A tree view at the left of the window, where you will see the list of buffers (at the moment, there are only five  of these: news feed, my wall, my audios, populars and recommended). These buffers are divided in two categories, posts and music. You could expand each category for seeing the child buffers. There are some additional buffers, timelines and chats, wich will be filled with timelines for your friends or with chats, when you  start or receive a chat session.
* A button for making a post to your wall.
* In audio buffers, Two buttons: Play and play all.
* A list where you will see the posts for the currently selected buffer.
* A status bar where the program will put some useful information about what it's doing at the moment.
* And a menu bar, which could be used for making a search for audio files in VK, or check for updates.

When socializer starts, it will try to load your news items, wall and audios. At the moment there are only a few supported actions for   these items:

* Audio files: You can play the currently selected song, view the song's details (including lyrics, if available), add or remove from your library, and download it to a desired place in your hard drive. You can find audio files in your news feed or in your own audios buffers.
* News feed's post: In your news feed buffer, you can press return in any post and socializer will open a new dialogue which can be different, depending in the kind of post you are when the return key was pressed.
* At the moment you can't open your wall posts.

### Making a post

When you press the post button, a new dialogue will show up. This dialogue allows you to post something in your wall. In this dialogue you have to write a message. You can translate your message and fix your spelling mistakes. Also you can post an URL address, socializer will try to add it as an attachment, so you will not have to worry about this. When you're ready, just press the send button and it'll be done.

### Working with posts in news feed

You can press the return key in any post in your news feed for opening a new dialogue with some information. The information and dialogue will be different if you are viewing a friendship's notification  (when someone has added some friends), an audio file, or a regular post.

If you open a regular post in your newsfeed, you will be able to see the comments in a list, indicate if you do like or dislike the post, or add a new comment.

For friend notifications, you can only view the new added friends in a list and  there are some kind of posts that aren't handled. It should be improved.

### Working with songs

If you want to play or view  audio's details, you'll have to navigate to the tree view, and, using the down arrow, look for "my audios", "populars" or "Recommendations". You will see two more buttons, play and play all. The play button will play the currently selected audio, and the play all button will play audios in the current buffer, starting with the current selected item. You can go to the song's list, look for a desired song and press the play button, or Ctrl+return, which is a keyboard shorcut. Take in to account that there are some keyboard shorcuts that only work in the list of items.

You can play audio from any buffer, just press ctrl+return for making the audio playback possible.

If someone has added multiple audios at once to his library, you will see something like this in your newsfeed: "(friend) has added 4 audios: audio 1, audio2, audio3 and audio4". You can press return in the  post for opening the audio's details dialogue, where you will be able to see a list with these audios. By default the first detected song is selected, which means that you could read its details by pressing tab, download or add it to your library. If you change the audio in the list, the information will be updated and you will see details and actions will take effect in the new selected audio.

When an  audio file is playing, you can press f5 and f6 for decreasing and increasing volume, respectively, or control+shift+return for play/pause.

If you want to see  some details for the selected audio file, you can do it by pressing the return key. You will be able to read some useful information  (title, artist, duration and the lyric, if available). Also you will be able to download the song to your hard drive, you have to press the download button in the details' dialogue.

When the download starts, you can close the details dialogue and check the status bar in the main window for seeing the current progress.

## menu Bar

You can go to the menu bar by pressing ALT. Right now, there are only two menus, buffer and help:

### Buffer menu

* New buffer: This submenu  allows you to create a new buffer, at the moment, you can create only a kind of buffer, an audio search. The audio search will be located in the music category and will have the last 299 results of your query. It isn't possible to delete the buffers until you restart the client.
* Update current buffer: perform an update operation in the selected buffer, which will retrieve the new items.
* Remove buffer: Tries to remove the current buffer. It only works with audio searches, because the default buffers shouldn't be removed.

The help menu is self explanatory.

## Contributing

If you are interested in this project, you can help it by [translating this program](https://github.com/manuelcortez/socializer/wiki/translate) into your native language and give more people the possibility of using it. Thank you in advance!

## contact

If you have questions, don't esitate to contact me in [Twitter,](https://twitter.com/manuelcortez00) or sending me an email to manuel(at)manuelcortez(dot)net. Just replace the words in parentheses with the original signs.