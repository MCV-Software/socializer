# Socializer's manual 

## Introduction

Socializer is an application to use [VK.com](https://vk.com) in an easy and accessible way with minimal CPU resource usage. Socializer will allow you to interact with the VK social network by giving you access to the most relevant features such as:

* Supports two factor authentication (2FA).
* Basic post creation in your wall (including photos).
* audio support.
* Post comments.
* like, unlike and repost other's posts.
* Open other's timelines so you could track their friends, posts or audio files.
* Basic chat features.

## Usage

In order to use socializer, you must have an account in the [VK](https://vk.com) website. The process for registering an account is very accessible and is not covered in this manual. In the documentation, it is assumed you have a registered account on VK and you are able to sign in in the website by providing your phone number or email address, and a password. You will require this data for signing in the application later.

## authorising the application

First of all, it's necessary to authorise the application so it can access your VK account and act on your behalf. The authorisation process is quite simple, and will be required only once. In order to start the authorisation process, you just need to run the executable file called "socializer.exe" (on some computers it will appear only as socializer, depending if windows explorer is set to display file extensions or not). You may like to place a Windows shortcut in your desktop for an easier access to the application.

If this is the first time you have launched socializer, you will see a message asking you whether socializer should connect through a proxy server, already configured in the application, or use the system network settings. This allows people from countries where VK is blocked to use the social network without having to look for a proxy server themselves. It is highly adviced to use the proxy server only if you are in need of it.

After the proxy message, you will see a new message dialog asking you to proceed with the account authorisation process. It consists in providing the authentication data you normally use to sign in VK. It is very important to know that this data will be stored in a folder called config, located in the same folder where the socializer files are. Your config folder is a very important storage for your authentication data, so you must be sure you never will share it with anyone, mostly because your data is stored as plain text (this will be fixed in a future release and your data will be properly encrypted). Socializer will need your authentication data for acting in your behalf and offering you a better experience that what it could do with a simple access token. You must provide your phone number or email address in the first text box, and your password in the second. When pressing OK, your data will be saved and the application will start to retrieve all the required information for showing your buffers. If you have two factor authentication configured in your account, you will see an additional dialog where you have to type the code provided by VK via SMS.

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

* Newsfeed post: It represents a post displayed in your "home" page on VK. It may contain a variety of information based in what you or your friends do. A newsfeed item may contain information about new audios added to your friend's library, new people added to friends, wall posts, reposts and new photos added. Depending on the kind of data VK has supplied, the item can open a dialog showing information about the post, a list displaying the people added to friends, or a dialog displaying information for every audio added to library. If a wall post contains a long message, only the first 140 characters will be displayed. You can open the post to read the full message in the dialog. Available options for this item are different depending in the information the item contains. You can open or view the profile of the user that generated the item, like, dislike or add a comment to a post.
* Wall post: Represent a post in an user's wall. This post will be similar to wall posts displayed in the newsfeed. If a wall post contains a long message, only the first 140 characters will be displayed. You can open the post to read the full message in the dialog. When opened (by pressing enter or the open option in the associated menu), it will show a dialogue where you can read the message, see how many times the post has been viewed by other users, interact with attachment files (by searching the list and pressing enter in the focused attachment to open it), see the photos included in the post, read information related to likes and times the post has been shared, read and reply to comments. Additionally, you can share the post, indicate you like it, or add a comment. You can cycle through every item in the dialog by pressing tab.
* Audio: It represent an audio uploaded to the VK'S platform. Actions available for this item are opening the audio in a dialog, add or remove it from your library, move the audio to a playlist, and play it. When opened, it will be displayed in a dialog allowing you to read the title of the song, artist name, duration and a few buttons: play, add or remove from your library and download. You can control playback of audio items from the buffer by using the player menu on the menu bar or the corresponding keyboard shortcuts.
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

* Post: this button opens up a dialogue box to write a post in the wall of the focused user. For example, if you are in the "my wall" buffer you will send a post to your own wall, but if you are in an user timeline the post will be sent to the owner of the timeline. You can upload an attachment  by pressing the "attach" button and choosing between uploading a  photo or audio file in the dialog which will appear, check spelling or translate your message by selecting one of the available buttons in the dialogue box. In addition, you can tag a friend in your post by pressing the corresponding button for that purpose. Also it is possible to configure the privacy settings for your post by  allowing all users or just your friends to read it. Press the send  button to send the post.
* Play: In audio buffers, plays the focused song. In video buffers, this button will open a web browser for playing the focused video, due to a limitation VK placed to third party developers with videos.
* Play all: In audio buffers, play all songs starting from the focused buffer, until the last item in the list.
* Send message: Send a message to a friend, which will open a conversation buffer if it does not exist already. Conversation buffers contain a full conversation, accommodating chat messages, between the current user and someone else. You can type your message in the provided box and press enter to send it to your friend. Additionally, You can upload an attachment  by pressing the "attach" button and choosing between uploading a  photo, audio file or record a voice message in the dialog which will appear, and open attachments sent in the focused message by pressing tab and finding them in the attachments list.

Bear in mind that buttons will appear according to which actions are possible on the list you are browsing.

## Menus

Visually, Towards the top of the main application window, A menu bar can be found which contains many of the same functions as listed in the previous section, together with some additional items. To access the menu bar, press the alt key. You will find five menus listed: application, Me, buffer, player and help. This section describes the items on each one of them.

### Application menu

* Create: opens a menu where you can create a new album. At the moment, only video albums are supported.
* Delete: opens a menu where you can delete an already existing album owned by yourself. Only video albums are supported at this time.
* Preferences: Opens a dialogue which lets you configure settings for the entire application.

### Me menu

* Profile: Opens a menu with several options to do in your profile:
    * View profile: Displays your profile in a dialog in the application.
    * Open in browser: Redirects you to your profile in vk.com.
* Set status message: Opens up a dialog where you can write your status message. The status message is displayed in your profile and can contain up to 140 characters.

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
* Report an error: opens up a dialogue box to report a bug by completing a small number of fields. Pressing enter will send the report. If the operation doesn't succeed the program will display a warning.

## Keyboard shortcuts

Socializer includes some keyboard shortcuts, available from any buffer (except empty buffers and conversations). Here you have the list of the available shortcuts:

* Enter: Execute the default action for the focused item. It may be opening a post, view friends added by someone else, view audio details or opening an user profile.
* Control + Enter: Play audio.
* Control + Shift+Enter: pause audio playback.
* F5: Decrease volume by 5%.
* F6: Increase volume by 5%.

## configuration

As described above, this application has a preferences dialogue accessible under the application menu. Here you have a brief description of the settings present in this dialogue.

### General tab

* Number of items to load for newsfeed and wall buffers: Allows you to specify how many items should be retrieved from VK in the newsfeed buffer and when opening walls for other users. Default and maximum is 100.
* Number of items to load in video buffers: Allows you to specify how many items should be retrieved from VK in video buffers. Default and maximum is 200.
* Load images in posts: Allows you to specify whether you want socializer to display all images when opening a post, or not. This can be useful for people with slow connections or not needing images.
* Update channel: allows you to specify how often you will receive updates for the program. There are two update channels available: Alpha channel, which contains unstable versions of the application and gets updates almost dayly, and stable, which contain tested and more stable versions of the program, but gets updates once in a month, approximately.

### Chat settings tab

* Show notifications when users are online/offline: These two checkboxes allows you to specify if you want socializer to notify you when someone is connected or disconnected in the VK network.
* Open unread conversations at startup: When enabled, Socializer will load any conversation with unread messages after started.
* Move focus to new conversations: When enabled, new conversations will be focused automatically right after being created.
* Notification type: This setting allows you to specify the notification type you prefer to use in socializer. The options are native and custom. Native notifications send a system notification every time someone is online or offline, while custom notifications play a sound and announce the notification in the screen reader only.

### Optional buffers tab

This section allows you to specify which buffers should be precreated every time socializer starts. This kind of buffers, namely audio playlists, video albums and communities, have a special way of being created. When a buffer of the previously mentioned types is created, the buffer is added to the corresponding section but no data is loaded from VK. In order to load the data for one of these buffers you have to press the load button present in the buffer. From this tab you can mark and unmark the buffers Socializer will create when it starts. By default, buffers for audio playlists, video albums and communities are not created automatically when Socializer starts.

## License and source code

Socializer is free software, licensed under the GNU GPL license, either version 2 or, at your option, any later version. You can view the license in the file named license.txt, or online at <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

The source code of the program is available at <https://code.manuelcortez.net/manuelcortez/socializer>.

## Contact

If you still have questions after reading this document, if you wish to collaborate to the project in some other way, or if you simply want to get in touch with the team, [join the Socializer's community in VK.](https://vk.com/socializer.club) You can also visit [The project website.](http://socializer.su)

## Credits

Socializer is developed and mantained by [Manuel Cortez,](https://manuelcortez.net) with contributions by [Anibal Hernandez](https://dragodark.com)

We would also like to thank the translators of Socializer, who have allowed the spreading of the application.

* English: Manuel Cortéz.
* Spanish: Manuel Cortéz.
* Russian: Дарья Ратникова.

Special thanks to Дарья Ратникова, as she also manages the Socializer's community in VK, translates the website and the documentation into Russian.