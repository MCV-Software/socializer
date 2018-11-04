# Changelog

## Changes in the current build ()

* Added two more buffers: "Followers" and "I follow", located in the people buffer, under "friendship requests".
* Added an experimental photo viewer. Will show options for seeing  the next and previous photo if the current post contains multiple images. Fullscreen button still doesn't work.
* Improved chats, now they should be more stable. Also you will be able to send the message by pressing enter in the text box. If you are trying to send the same message multiple times, you will be warned.
* Added video management (my videos, video albums and video search). For playing videos, you will be redirected to a website in your browser due to the VK'S policy.
* Added a setting that allows you to specify if you want socializer to load images when you are opening posts. It could be useful for slow connections or those who  don't want images to be loaded.
* Added basic tagging for users in posts and comments. You can tag only people in your friends buffer.
* Added a basic user profile viewer.
* Added support for listening voice messages in chats. Currently it is not possible to send them, until the new API will be released.
* For now, all features related to audio playback have been disabled.
* Fixed an error that was making Socializer unable to display chat history properly. It was showing the first 200 items in a  conversation instead the last 200 items. Now chat will be displayed accordingly.

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

---
© 2016, manuel cortéz.