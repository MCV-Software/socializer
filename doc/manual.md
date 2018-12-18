Socializer's manual 

## Introduction

Socializer is an application to use [VK.com](https://vk.com) in an easy and accessible way with minimal CPU resource usage. Socializer will allow you to interact with the VK social network by giving you access to the most relevant features such as:

* Basic post creation in your wall (including photos).
* (limited) audio support. (*)
* Post comments.
* like, unlike and repost other's posts.
* Open other's timelines so you could track their friends, posts or audio files.
* Basic chat features.

\* Audio support in socializer is limited due to the restrictions VK has decided to apply for third party applications on december 2016.

## Usage

In order to use socializer, you must have an account in the [VK](https://vk.com) website. The process for registering an account is very accessible and is not covered in this manual. In the documentation, it is assumed you have a registered account on VK and you are able to sign in in the website by providing your phone number or email address, and a password. You will require this data for signing in the application later.

## authorising the application

First of all, it's necessary to authorise the application so it can access your VK account and act on your behalf. The authorisation process is quite simple, and will be required only once. In order to start the authorisation process, you just need to run the executable file called "socializer.exe" (on some computers it will appear only as socializer, depending if windows explorer is set to display file extensions or not). You may like to place a Windows shortcut in your desktop for an easier access to the application.

If this is the first time you have launched socializer, you will see a message dialog asking you to proceed with the account authorisation process. It consists in providing the authentication data you normally use to sign in VK. It is very important to know that this data will be stored in a folder called config, located in the same folder where are the socializer files. Your config folder is a very important storage for your authentication data, so you must be sure you never will share it with anyone, mostly because your data is stored as plain text (this will be fixed in a future release and your data will be properly encrypted). Socializer will need your authentication data for acting in your behalf and offering you a better experience that what it could do with a simple access token. You must provide your phone number or email address in the first text box, and your password in the second. When pressing OK, your data will be saved and the application will start to retrieve all the required information for showing your buffers.

Once started, the application will start loading your data (posts, audio files, conversations, friends). When done, it will show you a notification indicating that the program is ready.

## General concepts

Before starting to describe Socializer's usage, we'll explain some concepts that will be used extensively throughout this manual.

### Buffer

A buffer is a list of items that will manage the data which arrives from VK, after being processed by the application. When you configure your account on Socializer and start it, many buffers are created. Each of them may contain some of the items which this program works with: Newsfeed posts, wall posts, audio and video files, friendship requests and conversations. According to the buffer you are focusing, you will be able to do different actions with these items.

All buffers will be updated in one of the following ways:

* Periodically: Most buffers containing posts, audio or video files and people, will be updated periodically to reflect the new additions to them. Updates will be every 2 minutes for every buffer, so if you posted something and did not see the post in the buffer, you may need to wait a moment. There is an option, located in the buffer menu on the menu bar, which allows you to trigger a manual update in the current buffer.
* Real time: Conversation buffers will be updated every time someone sends a message to you. When an user sends you a message, if there is not a conversation buffer created to receive the message, a new conversation buffer will be opened automatically and the message will be placed on it. If you already have an opened conversation for the user sending the message, the message will be placed at the end of the buffer. A different sound will indicate whether a new conversation has been opened or an existing buffer gets updated.

### item

An item is an element representing some data provided by VK. Items are separated in buffers which stores items of the same type: Audio buffers will contain only audio files, wall buffers will be full of wall posts. The only exception to this rule is the newsfeed buffer, which can contain different kind of items. Actions are available in a per-item basis, allowing certain items to be treated differently than others and showing different dialogs, depending in the kind of data VK sends for them. All items show a menu with their available actions by focusing them in the list and pressing the menu key or a right mouse click.

The following is a brief description of the kind of items socializer can work with, and what actions are available for those.

* Newsfeed post: It represents a post displayed in your "home" page on VK. It may contain a variety of information based in what you or your friends do. A newsfeed item may contain information about new audios added to your friend's library, new people added to friends, wall posts, reposts and new photos added. Depending on the kind of data VK has supplied, the item can open a dialog showing information about the post, a list displaying the people added to friends, or a dialog displaying information for every audio added to library. Take into account that it is not possible to play an audio item from the newsfeed buffer due to limits placed by VK, however, you may add it to your library and play it from your "my music" folder. If a wall post contains a long message, the first 140 characters will be displayed only. You can open the post to read the full message in the dialog. Available options for this item are different depending in the information the item contains. You can open or view the profile of the user that generated the item, like, dislike or add a comment to a post.
* Wall post: Represent a post in an user's wall. This posts will be similar to wall posts displayed in the newsfeed. If a wall post contains a long message, the first 140 characters will be displayed only. You can open the post to read the full message in the dialog. When opened (by pressing enter or the open option in the associated menu), it will show a dialogue where you can read the message, see and interact with attachment files (by searching the list and pressing enter in the focused attachment to open it), see the photos included in the post, read information related to likes and times the post has been shared, and read all comments. Additionally, you can share the post, indicate you like it, or add a comment. You can cycle through every item in the dialog by pressing tab.
* Audio: It represent an audio uploaded to the VK'S platform. Actions available for this item are only opening the audio in a dialog and play it due to limitations in access to audio features. When opened, it will be displayed in a dialog allowing you to read the title of the song, artist name, duration and a few buttons: play and download. You can control playback of audio items from the buffer by using the player menu on the menu bar.
* Video: It represent a video uploaded to the VK'S platform. Actions available for this item are opening the video in your default web browser and move it to a video album. When opened, it will open a web browser and play the video automatically due to VK limitations in access to video files.
* person: It contains information about a VK user, this item is present in all buffers under the "people" category. Actions available for this item are view user profile, send message and create a timeline, which is a special buffer to track all posts, friends or audios owned by the user. When opened, it will display the profile of this user in a dialog and will provide actions to send a message to the user, or view other sections of her/his profile.
* Message: A message appears only in conversation buffers and represents a chat message. It may include a list of attached files that will be displayed in a separated list. You can tab to that list (from the history) and press enter in the attached file you want to open. Chat items are marked as read automatically as soon as they are focused.

## Main interface

The graphical user interface of Socializer consists of a window containing:

* a menu bar accomodating five menus (application, Me, buffer, player and help),
* One tree view,
* One list of items
* Some buttons, depending which is the focused buffer.

The actions that are available for every item will be described later.

In summary, the GUI contains two core components. These are the controls you will find while pressing the Tab key within the program's interface, and the different elements present on the menu bar.

### Buttons in the application

* Post: this button opens up a dialogue box to write a post in your wall. For the moment, only posting in your own wall is supported. You can upload a picture by pressing the "attach" button and the photo button in the dialog which will appear, check spelling or translate your message by selecting one of the available buttons in the dialogue box. In addition, you can tag a friend in your post by pressing the corresponding button for that purpose. Also it is possible to configure the privacy settings for your post by  allowing all users or just your friends to read it. Press the send  button to send the post.
* Play: In audio buffers, plays the focused song. In video buffers, this button will open a web browser for playing the focused video, due to a limitation VK placed to third party developers with videos.
* Play all: In audio buffers, play all songs starting from the focused buffer, until the last item in the list.
* Send message: Send a message to a friend, which will open a conversation buffer if it does not exist already. Conversation buffers contain a full conversation, accommodating chat messages, between the current user and someone else. You can type your message in the provided box and press enter to send it to your friend. Additionally, you can add an attachment (for the moment, only attaching an audio file from your library is supported) and open attachments sent in the focused message by pressing tab and finding them in the attachments list.

Bear in mind that buttons will appear according to which actions are possible on the list you are browsing.

## Menus

Visually, Towards the top of the main application window, can be found a menu bar which contains many of the same functions as listed in the previous section, together with some additional items. To access the menu bar, press the alt key. You will find five menus listed: application, Me, buffer, player and help. This section describes the items on each one of them.

### Application menu

* Create: opens a menu where you can create a new album. At the moment, only video albums are supported.
* Delete: opens a menu where you can delete an already existing album owned by yourself. Only video albums are supported at this time.
* Preferences: Opens a dialogue which lets you configure settings for the entire application.

### Me menu

* Profile: Opens a menu with several options to do in your profile:
    * View profile: Displays your profile in a dialog in the application.
    * Open in browser: Redirects you to your profile in vk.com.

### Buffer menu

* New timeline: Lets you open a user's timeline by choosing the user in a dialog box. You can choose which items you want to track: wall posts, friends or audio items. It is created when you press enter. If you invoke this option relative to a user that has no items of the kind you specified, the operation will fail. If you try creating an existing timeline the program will warn you and will not create it again.
* Search: Shows a menu where you can search for audios or videos on VK. Search results will be created in a new buffer inside "music" or "videos".
* Update buffer: Performs a manual update operation in the buffer, which will retrieve all new items present in the social network since the last update.
* Load previous items: This allows more items to be loaded for the specified buffer. Bear in mind that not all buffers support this setting.
* Destroy: dismisses the list you're on, if possible.

### Player menu

* Play: Plays the currently focused audio item, if the current buffer contains audio files. If not, plays the focused audio in the "my music" buffer.
* Play all: Plays all audio items in the current buffer or the "my music" buffer, starting by the currently focused audio item until the last audio in the list.
* Stop: Stops audio playback.
* Previous: Plays the previous audio in the buffer or the last item in the list, if the current audio was the first on the buffer.
* Next: Plays the Next audio in the buffer or the first item in the list, if the current audio was the last on the buffer.
* Shuffle: Plays all audios in the current buffer or the "my music" buffer shuffled.
* Volume up: Increases volume by 5%.
* Volume down: decreases volume by 5%.
* Mute: Mutes audio playback, setting volume to 0%.

### help menu

* About Socializer: shows the credits of the program.
* Documentation: opens up this file, where you can read some useful program concepts.
* Check for updates: every time you open the program it automatically checks for new versions. If an update is available, it will ask you if you want to download the update. If you accept, the updating process will commence. When complete, Socializer will be restarted. This item checks for new updates without having to restart the application.
* Changelog: opens up a document with the list of changes from the current version to the earliest.

## Keyboard shortcuts

## configuration

### The general tab

### The chats tab

## License and source code

Socializer is free software, licensed under the GNU GPL license, either version 2 or, at your option, any later version. You can view the license in the file named license.txt, or online at <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

The source code of the program is available at <https://code.manuelcortez.net/manuelcortez/socializer>.

## Contact

If you still have questions after reading this document, if you wish to collaborate to the project in some other way, or if you simply want to get in touch with the application developer, follow the VK account of [Manuel Cortez.](https://vk.com/manuelcortez) You can also visit [The project website.](https://manuelcortez.net/socializer)

## Credits

Socializer is developed and mantained by [Manuel Cortez,](https://manuelcortez.net) with contributions by [Anibal Hernandez](https://dragodark.com)

We would also like to thank the translators of Socializer, who have allowed the spreading of the application.

* English: Manuel Cortéz.
* Spanish: Manuel Cortéz.
* Russian: Valeria K.