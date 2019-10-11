# Changelog

## News in this  version

### New additions

* Socializer is now more tolerant to internet issues. When attempting to create a wall post, comment, topic or send a chat message, if the data is unable to be posted to VK, socializer will allow you to try to post it again, giving you the opportunity to edit or copy the text of the post in case you want to save it for later.
* when selecting multiple audio files in audio buffers, multiple actions can be performed in all items, these actions are present in the contextual menu of the buffer (namely play, add/remove from the library and move to a different playlist). This means you can select all the audios you want and Socializer will perform the selected options in all items, making it a bit easier to operate with multiple songs.
* Now it is possible to like and see who liked a comment when displaying it individually. This applies to comments in wall posts and topics.
* Now it is possible to choose how many items Socializer will load in conversation buffers, from the General tab in the preferences dialog. The default value is 50 items, and the maximum value is 200.
* There is a new tab called buffer settings, in the preferences dialog. Settings related to how many items should be loaded in certain buffer types have been moved to this tab, so it will separate better the configuration options in the application.
* Added management of the Blacklist on VK. Users can be blocked from people buffers (friends, online, or any buffer inside friend requests). You can access the blacklist from the application menu, located in the menu bar. From there, you can unblock any previously blocked user.
* In the new timeline dialog, it is possible to create video buffers.

### bugfixes

* Fixed an error that was causing socializer to not update the "Online friends" buffer if chat notifications were disabled.
* Fixed an error that was making Socializer unable to attach audio files from the computer, if the file does not include correct ID3 TAGS.
* Fixed a traceback that was being logged when attempting to load an image but cancel the dialog for attaching it.
* Fixed an error that was making Socializer to fail when loading the newsfeed buffer, thus not loading any other buffers. This error was caused due to VK sending a new object type representing push subscriptions. The item is ignored by Socializer so it will not break the newsfeed buffer anymore.
* Fixed an error that was making the status bar to not fit the full size of the Window. This was cutting the messages placed on it, now, all messages are displayed properly again.
* fixed an unhandled condition when playing a song and voice message at the same time, that was potentially making Socializer to stop loading certain buffers.
* fixed an error that was making socializer unable to parse video data, thus video buffers were impossible to be loaded.

### Changes

* Less confidential user data will be send to the logs, so it will be much safer to pass logs publicly.
* automatic update checks will be disabled if using socializer from the source code.
* it is possible to post in an user's wall by using the post button located next to the user, in people buffers. This applies only to online users and list of friends.
* When displaying a profile, information about mobile and home phone is displayed in the basic information tab.
* In wall posts, all comments, including replies, will be displayed in the same list. Before, you had to open a comment to read its replies. When a new comment is posted by the current user, the list of comments will be reloaded and new additions will be fetched and sorted properly.

## changes in Versions 0.21 and 0.22 (14.07.2019)

### New additions

* Added "post in groups" feature. In order to do so, you need to load the posts for the group where you want to send something. Once loaded, go to the post button in the group's wall and select whether you want to post in the group's behalf or as yourself.
* In all audio buffers, it is possible to select individual tracks to be played together. In order to do so, you need to press space to start the selection of items. When selected, the item will emit a sound to indicate the change. Press space in all items you want to select/unselect. When you're focusing an already selected item it will play a sound to indicate that it is already selected. Once you're done with your selection, pressing enter in the list of tracks will start the playback of the list of items you have selected. This is a very experimental feature. More actions can be supported based in this selection method if it proves to be useful.
* In conversation buffers, it is possible to display and open wall posts sent as attachments in messages.
* In people buffers, it is possible to create a new timeline by using the context menu while focusing an user. This method will create the buffer for the selected user, as opposed to creating the buffer from the menu bar, where you have to type the username or find it in a list.

### bugfixes

* Fixed an error with two factor authentication in the recent socializer version. Now it works reliably again.
* Fixed an error when trying to attach a photo to a wall post. The error was fixed in the [vk_api](https://github.com/python273/vk_api) module and the fix was sent to the developer of the library, so he will be able to merge it in the next version. In the meantime, socializer already includes the fix for this method, so you can upload photos to wall posts normally.
* Fixed an error retrieving some group information for the current session.
* When posting in a topic, links will be posted properly.


### Changes

* the audio player module has received some improvements:
    - When there is something being played, the label of the "play" button, located in all audio buffers, will change automatically to "pause". When pressed, it will pause the song instead of starting the playback again since the beginning.
    - The last change will work also in the dialog for displaying audio information. Now it's possible to play and pause an audio from such dialog.
    - When playing a voice message, if a song is playing already socializer will decrease the volume so you can hear the voice message well enough. Some seconds after the message has finished, the song's volume will be restored.
* In audio buffers, you will play the focused audio when pressing enter in the item, instead of opening the audio information dialog.
* Removed some old keystrokes in socializer buffers due to better alternatives. The reason for this change is that currently you don't need to be focusing an item in a buffer for being able to use the alternative keystrokes, which makes those a better implementation.
    - Control+Enter and control+Shift+Enter: superseeded by Control+P for playing (and pausing) the currently focused audio.
    - F5 and F6: superseeded by Alt+down and up arrows for modifying volume.

## changes in version 0.20 (25.04.2019)

### New additions

* For users with multiple soundcards, there is a new tab in the preferences dialogue of Socializer, called sound. From there, you can define which soundcard will be used for input and output. [#25,](https://code.manuelcortez.net/manuelcortez/socializer/issues/25)
* the audio player can seek positions in the currently playing track. You can use the menu items (located in the main menu) or use the new available keystrokes dedicated to the actions. Seeking will be made in 5 second intervals.
    * Alt+Shift+Left arrow: Seek 5 seconds backwards.
    * Alt+Shift+Right arrow: Seek 5 seconds forwards.
* it is possible to select the language used in socializer from the preferences dialog. When changing the language, the application must be restarted for the changes to take effect.
* A new option, called open in vk.com, has been added in the context menu for almost all objects (items in home timeline, walls, documents, people, group topics and in buffers for conversations). This option will open the selected item in the VK website.
* when opening the list of friends added by an user, you can display the context menu from an item on the list and view the user profile, open it in VK.com, among other actions. [#8,](https://code.manuelcortez.net/manuelcortez/socializer/issues/8)
* When displaying a post, if you press enter in the button indicating how many people liked or shared the post, Socializer will display the listt of people who have liked or shared it. You can use the context menu in the list to do certain actions. [#38,](https://code.manuelcortez.net/manuelcortez/socializer/issues/38)
* it is possible to retrieve more items for conversation buffers. Due to API limitations, it is possible to load up to the last 600 messages for every conversation. Take into account that the process of loading more items takes some time. You will hear a message when the process is done.
* It is possible to delete entire conversations from the buffer's tree, by using the menu key and selecting "delete conversation". The conversation will be removed from VK.
* When loading a topic in a group, socializer will display the latest 100 messages. In order to load more messages, you will find a button that will load the previous 100 messages present in the topic, or the amount of messages not loaded yet.

### bugfixes

* All spelling dictionaries are included by default for the following languages: Russian, English, German, French, italian, Polish, spanish and Turkish. Before, some dictionaries were missing and the spelling checker was failing.
* Fixed an error in the default configuration template used for new sessions in the application. This error was making Socializer to fail when loading any conversation buffer.
* Fixed an error in the algorithm to detect friends disconnecting from VK. This problem was interrupting the connection with  the chat server every time it was happening, thus chat server's connection should be more reliable now.
* The audio player should behave better in situations where a song is interrupted. Before, if you pressed "next song" while the currently playing sound was interrupted due to internet connection issues, two or more songs were played at the same time.
* The bug reporting feature works normally again.

### Changes

* Updated method for accessing audio files due to the latest changes on VK apps.
* When changing volume of the playing audio, it will decrease or increase the volume by 2% instead of 5%. 
* Read confirmations will be sent to VK as soon as you read the message. Before, read confirmations were being sent every 3 minutes to the social network.

## Changes in version 0.19 (13.03.2019)

* Added a new buffer called documents. When loading the buffer, it will contain all documents owned by the current user. The context menu of any item will allow you to download the document to your computer or remove it from VK.
* A new buffer, called online, has been added in the friends section. It contains friends currently connected to VK. Items in this buffer will be added as soon as new friends are online in the social network, and will be removed when friends are offline. This buffer needs a lot of testing. Please report any possible inconsistency on this method.
* Added new options to open the config and logs folder, these options are located in the help menu and may be useful during error reporting.
* Added experimental support to "subscribers" buffer, inside frienship requests. This shows friend requests that have been declined by the current user.
* the message when an user is typing in conversation buffers will be announced only if the socializer window is focused.
* In "my audios" buffer, there is a button that allows a direct audio upload from your computer. The audio will be placed in your library.
* Added experimental support to user and community polls:
    * If the poll is already closed or the user has send a vote to the poll previously, it will display only the results of the poll.
    * Otherwise it will display a dialog from where the user can vote in the current poll.
* Fixed an error in Socializer that was making it unable to detect unread messages properly.
* Socializer should save all tracebacks directly to error.log instead of displaying an error message during exit. ([#27,](https://code.manuelcortez.net/manuelcortez/socializer/issues/27))
* When displaying user profiles, fixed an error where a married person without specifing relation partner would cause an error in the program. ([#29,](https://code.manuelcortez.net/manuelcortez/socializer/issues/29))
* Socializer will load all conversations during startup, not only conversations with unread messages.
* Added new global keystrokes, available in the main window.
    * Alt + up/down arrows: Increase / decrease volume.
    * Alt + Left/down arrows: Play previous and next song if playing an audios buffer.
    * Control + P: Play/pause.
    * control+Shift+P: Play all.
* Fixed an error in the audio player that was skipping the first track if you were in the last song and pressed "play next" in the menu bar or via the keystroke.
* Chats with unread messages will be placed at the top of the chats section. When a chat buffer receives a new message, socializer will move  the buffer to the first position in the chats list. This should make easier for everyone to determine which chats contain unread items. ([#24,](https://code.manuelcortez.net/manuelcortez/socializer/issues/24))
* In dialogs for displaying posts and comments, and also in the two edit boxes present in chat buffers, it is possible to select all by pressing Control+A.
* Now it is possible to remove friends directly from the friends buffer. There is a new option for this purpose in the context menu for the focused friend. After being removed, the person will be placed in the subscribers buffer.
* Deleted posts will display an error message when trying to view details about those. Before, the dialog was created and left blank.
* Improvements in audio features present in Socializer:
    * The audio search feature has received improvements: Now it is possible to indicate wether the search will be performed by title or artist, and select to sort the results by duration, popularity or date of addition to VK.
    * Now it is possible to create and delete audio albums again.
    * Fixed errors when moving songs to albums. Now everything works as expected.
* Added documents to the list of supported files when adding attachments to a wall post or private message.
* It is possible to enable or disable proxy from the preferences dialog. The application must be restarted for this change to take effect.
* Fixed an error that was making Socializer unable to display the changelog properly, when opened from the help menu. ([#21](https://code.manuelcortez.net/manuelcortez/socializer/issues/21))
* When receiving chat messages and in some other situations, socializer will display all characters properly. Before, usernames were rendered using the internal code VK uses for them, and some unicode characters were displaying their HTML representation.
* It is possible to retrieve previous items for the home buffer and walls (current user's wall and any other timeline):
    * For the home buffer, only a limited amount of items (around 700) can be loaded, supposedly due to VK API limits.
    * For walls, all posts should be possible to be loaded, however, testing with walls containing more than 2000 posts are not performed yet.
* Added improvements to groups:
    * It is possible to load topics, audios, videos and documents for a group. In order to do so, you need to go to the group buffer and press the menu key, or right mouse click, in the tree item representing the group. New buffers will be created inside the current group's buffer.
    * You can create or delete all buffers for groups by pressing the menu key or right mouse click in the "communities" buffer.
    * There is  support for group topics. When opening them, they will be displayed as a list of posts. You can like or reply to such posts, as well as adding new posts in the topic.
* Authentication errors should be handled gracefully by the application:
    * When there is a password change, Socializer must be reauthorized again. An error message will indicate this if the user forgot to do that. After the error, the app will be restarted, prompting the user to introduce the new data for authorizing the application.
    * If the user introduced incorrect or invalid data, Socializer will display an error and prompt the user again for valid information.
    * If there is a connection problem when opening Socializer, it will display an error and inform the user about the issue.

## Changes in version 0.18 (21.01.2019)

* Changed authentication tokens in Socializer. It is mandatory to download a fresh copy of socializer and start a new configuration for your account.
* Stable versions of Socializer are built with Python 3. Previous versions are built with Python 2, however support for Python 2 will be dropped very soon.
* There is an installer file for Socializer, available in our downloads page. Installed version of Socializer will be more confortable for some people.
* For users from countries where VK is not allowed, Socializer includes a proxy to bypass country restrictions. The first time you start socializer, it will ask you whether you need a proxy or not. It is suggested to use a proxy only if you need it.
* Now it is possible to post in someone else's wall. When viewing a timeline of an user, the "post" button will post in his/her wall. To post in your own wall, you'll need to go to the newsfeed or your own wall and press the post button.
* If you are not allowed to post in someone's wall, the post button will not be visible.
* A new option for deleting wall posts has been added to the context menu in newsfeed and walls (current user's wall and timelines). This option will be visible only if the current user is allowed to delete the focused post.
* Socializer will be able to handle all users correctly. Before, if an user that was not present in the local storage system was needed, the program was displaying "no specified user". ([#17,](https://code.manuelcortez.net/manuelcortez/socializer/issues/17))
* It is possible to use user domains (short names for users) to create timelines. Just write @username and the program will create the needed timeline, regardless if the user is present in your friend list. ([#18,](https://code.manuelcortez.net/manuelcortez/socializer/issues/18))
* When displaying someone's profile, the dialog should be loaded dramatically faster than before. A message will be spoken when all data of the profile is loaded.
* When opening a timeline, if the current user is not allowed to do it, an error message should be displayed and the buffer will not be created. Before the buffer was partially created in the main window. ([#22.](https://code.manuelcortez.net/manuelcortez/socializer/issues/22))
* Added basic support to handle group chats. At the current moment it is possible to receive and reply to chat messages only. Chat groups will be placed inside the conversations section. ([#23.](https://code.manuelcortez.net/manuelcortez/socializer/issues/23))
* It is possible to delete a conversation buffer from the buffer menu. Deleting a conversation will only dismiss the buffer, no data is deleted at VK.
* During the first start of Socializer, an invitation will be shown to join the Socializer's group in case the current user is not already a member.
* It is possible to see how many people has read a wall post when showing it in the dialog. ([#28.](https://code.manuelcortez.net/manuelcortez/socializer/issues/28))
* A new tab has been added to the preferences dialog. From the new section, it is possible to control whether socializer should create buffers for the first 1000 audio albums, video albums and communities when starting.
* Added functionality regarding comments in wall posts:
    * when reading a post, you can press enter in any comment to display a dialog from where it is possible to view attachments, translate, check spelling or reply to the thread. If there are replies made to this comment, these will be visible in a section called replies. Pressing enter in a reply will also open the same dialog.
    * A new "replies" field has been added to the comments' list.
    * When writing a comment, it is possible to do the same actions available for a post (translate, spell checking and adding attachments).

## Changes in version 0.17 (01.01.2019)

* Added support for Two factor authentication (2FA). ([#13,](https://code.manuelcortez.net/manuelcortez/socializer/issues/13))
* Added update channels in socializer. You can subscribe to the "stable" or "alpha" channel from the preferences dialog and you will receive updates published for those:
    * The stable channel will have releases every month, approximately, and is the channel where the code will be more tested and with less bugs. All support and help will be provided for the stable versions only.
    * The alpha channel will have releases every time a change is added to socializer, it may even include several releases in the same day, but we will try to release only a new version every day. Support will not be provided for alpha versions, as they will be used to test the latest code in the application.
* Now it is possible to send voice messages from socializer. Voice messages are available from the "add" button in any conversation buffer.
* tokens generated by socializer will never expire. ([#3,](https://code.manuelcortez.net/manuelcortez/socializer/issues/3))
* In order to use all methods available in VK, socializer will use tokens of kate mobile for Android. It means you may receive an email by saying that you've authorised Kate for accessing your account from an Android device.
* Audio albums are loaded correctly.
* It is possible to play audios added by friends appearing in the news feed.
* Adding and removing an audio file to your library works.
* Unread messages will play a sound when focused.
* Unread messages will be marked as read when user focuses them.
* Socializer will handle restricted audio tracks. Restricted songs are not allowed to be played in the user's country. Before, playing a restricted track was generating an exception and playback could not resume. Now, playing an audio track will display an error notification.
* Fixed an error when people were trying to open a post in an empty buffer, or accessing the menu when there are no posts in the buffer.
* Now Socializer will not send a notification every 5 minutes.
* the chat widget now is a multiline text control. It means it is possible to add a new line by pressing shift+Enter, and send the message by pressing enter.
* Socializer should handle connection errors when loading items in buffers and retry in 2 minutes. Also, connection errors in the chat server are handled and chat should be able to reconnect by itself.
* When trying to add an audio or video to an album, if the current user does not have any album, it will display an error instead of a traceback.
* Added popular and suggested songs. This will not work when using alternative tokens.
* Now it is possible to update the status message, located in your profile.
* Now it is possible to upload an audio from your computer when adding attachments in a wall post. When adding attachments to a post or message in a conversation, you will have two options: upload from your computer and add a file from your VK profile.
* Updated Russian translation: thanks to Дарья Ратникова.
* Fixed some conditions, especially when rendering items in feeds, that were making the client to crash.
* new versions will include documentation and changelog.
* A new option for reporting issues directly from the help menu has been added. Issues will be publicly available in the [Project Issues page](https://code.manuelcortez.net/manuelcortez/socializer/issues)

## Changes in version 0.16 (13.12.2018)

* Added two more buffers: "Pending requests" and "I follow", located in the people buffer, under "friendship requests".
* Added an experimental photo viewer. Will show options for displaying  the next and previous photo if the current post contains multiple images. Fullscreen button still doesn't work.
* Improved the chat features present in the application. Read documentation to get a full understanding about how it works now.
* Added video management (my videos, video albums and video search). For playing videos, you will be redirected to a website in your browser due to the VK'S policy.
* Added a setting that allows you to specify if you want socializer to load images when you are opening posts. It could be useful for slow connections or those who  don't want images to be loaded.
* Added basic tagging for users in posts and comments. You can tag only people in your friends buffer.
* Added a basic user profile viewer.
* Added support for listening voice messages in chats. Currently it is not possible to send them.
* Fixed an error that was making Socializer unable to display chat history properly. It was showing the first 200 items in a  conversation instead the last 200 items. Now chat will be displayed accordingly.
* Changed the chat history widget from list of items to a read only text box, similar to how it was displayed in skype. Now the widget should be fully visible and messages will work in the same way.
* It is possible to play songs sent in a chat message by opening them from the attachments panel.
* Reimplemented most of the audio playback methods (audio albums buffer still not working).
* Added some notifications and chat notifications when friends are online and offline. Most notifications can be configured from settings.

## Changes in build 2016.07.08 (08/07/2016)

* Removed platform from "last seen" column in the friends list as it could cause some problems and it was being not so exact.
* Now deleted audios are not parsed and displayed as "audio removed from library". They are silently ignored.
* It's possible to open a friends timeline for others.
* Fixed some strange bugs in the built version.
* Deactivated accounts will not cause problems in friends lists. They will be displayed as deactivated, wich means that it'll be impossible to interact with those accounts.
* When opened, the client will set online for the user account, it'll inform VK that this user is currently online. This parameter will be updated every 15 minutes, as stated in the API documentation.
* When opened, socializer will try to create chat buffers for all unread messages.
* Update some information on certain posts when an item is selected. For example, update the date of a post.
* Read messages will be marked as read in the social network, so it'll cause that your friends could see that you have read the message and socializer will not load  chat buffers with read messages at startup.
* Included a brief   manual in the help menu. Currently available only in English.
* Included a context menu in list items. Currently there are functions not available. Menu for chat buffers is not implemented yet.
* Implemented audio album load (in the music  buffer), creation (in the application menu) and deletion (in the application menu, too).
* audios can be moved to albums by pressing the menu key or doing a right click in the item, and selecting "move to album". Audios will be added to the album in the next update (there is a programmed update every 3 minutes), or you can update the buffer manually (from the buffer menu in the menu bar). This option will be available in audio buffers (searches, popular and recommended audio buffers, and audio timelines).
* Albums will be empty at startup. In order to get the album's audios, you'll have to navigate to the album and press the button "load". It'll load the needed information for displaying and playing the added songs 
* If the config is invalid (for example you changed email or phone in the VK site and didn't changed that in Socializer, or just entered invalid credentials), the program will display an error with instructions for fixing the problem.
* Now is possible to press enter in the password or email/phone field and it'll do the action of the OK button.
* If you have set russian as the main language in the VK site, you'll see names in genitive and instrumental cases in certain phrases.
* Updated russian and spanish translations.

## Changes on build 2016.05.25

* Added grouped controls in the audio searches dialogue. It will be more accessible so screen readers could detect and read the label for radio buttons.
* Added  documents to the list of supported attachments in the post viewer. The action for this kind of attachments is to open the default web browser, pointing to the URL address of that file.
* Now It's possible to add photos to the wall, by uploading files to the VK servers. Check the attachments button in the new post dialogue for this. Basically it is possible to add some photos and when the post is sent, photos will start to be uploaded before. At the moment it is not possible to add descriptions to photos. Take in to account that photos will be uploaded when the send button is pressed and the post could take some time before being posted.
* Added a new option to the menu bar: new timeline. It allows to create a special buffer for a selected user. This buffer could be an audio or wall buffer, when created, the buffer will be updated with items for the specified user or community.
* Added an user selection control. In dialogues  where an user must be selected, there will be an edit box with a selected name. You need to start writing for changing this name, or just press the down arrow for looking in the users' database. You can start writing and then press the down arrow, so you will see the closest result  to the name you was writing. For example if you want to write manuel, you could write m, a, n, u, and press the down arrow, and you will see the full name in the edit box. Take in to account that you have to make sure that you write a valid user name in the box, otherwise you will see an error.
* Posts from twitter are displayed in a better way (newline characters (\n) are handled properly instead being displayed).
* In the play all function, everything should be cleaned before start the new playback.
* Now links included in text of a comment are included as attachments (links are "untitled" because it isn't possible to retrieve information for every link without performance issues). This is especially useful when someone posts a link from Twitter.
* Chat support: There is a new kind of buffer, named chat buffer, wich allows you to have a conversation with someone of your friends. If you receive a message while socializer is opened it will create a chat buffer under chats with the last 200 messages between you and your friend. You can send a message by writing in the edit box and pressing send or enter. At the moment chats buffers can't be removed. Will be added this possibility in the near future.
* Added your friendlist as a buffer. You can create chats from there by using the send message button.

## Changes for build 2016.04.5 (5/04/2016)

* Updated russian and spanish translations.
* Fixed minor bugs in the likes button for posts.
* Now it's possible to open  wall posts by pressing enter, as newsfeeds' posts.
* It's possible to see reposts in the news and wall buffers, and the post displayer (when you press enter in a post) shows the full post story.
* Added "load previous items" in the main menu. It should work for wall and news feed. This feature is not available in audio buffers due to API limits.
* Added more options in the search audio  dialog. Now users could use more parameters and searches will be more precise.
* Added a new attachments' list. When a post is opened, this list will show up if there are attachments in the current post (attachments are audio, photos, video and links). You will be able to interact with the supported data (at the moment only photos, videos, audio and links are supported, more will be added in future).
* Added a changelog  file which could be opened from the help menu.
* Added a preferences dialogue and a new application menu in the menu bar. From this dialogue you can change the number of items to be loaded for every buffer.