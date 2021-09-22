# -*- coding: utf-8 -*-
""" Attachment controller for different kind of posts in VK.
this controller will take care of preparing data structures to be uploaded later, when the user decides to start the upload process by sending the post.
"""
from __future__ import unicode_literals
import os
import logging
import interactors
import views
from mutagen.id3 import ID3
from mutagen.id3._util import ID3NoHeaderError
from sessionmanager.utils import seconds_to_string
from . import audioRecorder, base

log = logging.getLogger(__file__)

class attachPresenter(base.basePresenter):
    """ Controller used in some sections of the application, it can do the following:

    * Handle all user input related to adding local or online files (online files are those already uploaded in vk).
    * Prepare local files to be uploaded once a post will be sent (no uploading work is done here, but structured dicts will be generated).
    * Parse online files and allow addition of them as attachments, so this controller will add both local and online files in the same dialog.
"""

    def __init__(self, session, view, interactor, voice_messages=False):
        """ Constructor.
@ session sessionmanager.session object: an object capable of calling all VK methods and accessing the session database.
        @voice_messages bool: If True, will add a button for sending voice messages.
        """
        super(attachPresenter, self).__init__(view=view, interactor=interactor, modulename="attach")
        self.session = session
        # Self.attachments will hold a reference to all attachments added to the dialog.
        self.attachments = list()
        self.run()

    def upload_image(self, image, description):
        """ allows uploading an image from the computer. Description will be used when posting to VK.
        """
        imageInfo = {"type": "photo", "file": image, "description": description, "from": "local"}
        self.attachments.append(imageInfo)
        # Translators: This is the text displayed in the attachments dialog, when the user adds  a photo.
        info = [_("Photo"), description]
        self.send_message("insert_attachment", attachment=info)
        self.send_message("enable_control", control="remove")

    def upload_audio(self, audio):
        """ Allows uploading an audio file from the computer. Only mp3 files are supported. """
        if audio != None:
            # Define data structure for this attachment, as will be required by VK API later.
            # Let's extract the ID3 tags to show them in the list and send them to VK, too.
            try:
                audio_tags = ID3(audio)
                if "TIT2" in audio_tags:
                    title = audio_tags["TIT2"].text[0]
                else:
                    title = _("Untitled")
                if "TPE1" in audio_tags:
                    artist = audio_tags["TPE1"].text[0]
                else:
                    artist = _("Unknown artist")
            except ID3NoHeaderError: # File doesn't include ID3 tags so let's assume unknown artist.
                artist = _("Unknown artist")
                title = os.path.basename(audio).replace(".mp3", "")
            audioInfo = {"type": "audio", "file": audio, "from": "local", "title": title, "artist": artist}
            self.attachments.append(audioInfo)
            # Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
            info = [_("Audio file"), "{title} - {artist}".format(title=title, artist=artist)]
            self.send_message("insert_attachment", attachment=info)
            self.send_message("enable_control", control="remove")

    def upload_document(self, document):
        """ allows uploading a document from the computer.
        """
        doc_info = {"type": "document", "file": document, "from": "local", "title": os.path.basename(os.path.splitext(document)[0])}
        self.attachments.append(doc_info)
        # Translators: This is the text displayed in the attachments dialog, when the user adds  a document.
        info = [_("Document"), os.path.basename(document)]
        self.send_message("insert_attachment", attachment=info)
        self.send_message("enable_control", control="remove")

    def upload_voice_message(self):
        a = audioRecorder.audioRecorderPresenter(view=views.audioRecorderDialog(), interactor=interactors.audioRecorderInteractor())
        if a.file != None and a.duration != 0:
            audioInfo = {"type": "voice_message", "file": a.file, "from": "local"}
            self.attachments.append(audioInfo)
            # Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
            info = [_("Voice message"), seconds_to_string(a.duration,)]
            self.send_message("insert_attachment", attachment=info)
            self.send_message("enable_control", control="remove")

    ####### ToDo: replace this with selector presenter when finished.
    def get_available_audios(self):
        # Let's reuse the already downloaded audios.
        list_of_audios = self.session.db["me_audio"]["items"]
        audios = []
        for i in list_of_audios:
            audios.append("{0}, {1}".format(i["title"], i["artist"]))
        return audios

    def take_audios(self, audios_list):
        list_of_audios = self.session.db["me_audio"]["items"]
        for i in audios_list:
            info = dict(type="audio", id=list_of_audios[i]["id"], owner_id=list_of_audios[i]["owner_id"])
            info["from"] = "online"
            self.attachments.append(info)
            # Translators: This is the text displayed in the attachments dialog, when the user adds  an audio file.
            info2 = [_("Audio file"), "{0} - {1}".format(list_of_audios[i]["title"], list_of_audios[i]["artist"])]
            self.send_message("insert_attachment", attachment=info2)
        self.check_remove_status()

    def remove_attachment(self, item_index):
        """ Remove the currently focused item from the attachments list."""
        log.debug("Removing item %d" % (item_index,))
        if item_index == -1: item_index = 0
        self.attachments.pop(item_index)
        self.send_message("remove_attachment", attachment=item_index)
        self.check_remove_status()
        log.debug("Removed")

    def check_remove_status(self):
        """ Checks whether the remove button should remain enabled."""
        if len(self.attachments) == 0:
            self.send_message("disable_control", control="remove")
