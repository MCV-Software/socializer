# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import widgetUtils
from pubsub import pub
from wxUI.dialogs import selector
from wxUI.menus import attachMenu
from . import base

class attachInteractor(base.baseInteractor):

    def insert_attachment(self, attachment):
        self.view.attachments.insert_item(False, *attachment)

    def remove_attachment(self, attachment):
        self.view.attachments.remove_item(attachment)

    def install(self, *args, **kwargs):
        super(attachInteractor, self).install(*args, **kwargs)
        widgetUtils.connect_event(self.view.photo, widgetUtils.BUTTON_PRESSED, self.on_image)
        widgetUtils.connect_event(self.view.audio, widgetUtils.BUTTON_PRESSED, self.on_audio)
        widgetUtils.connect_event(self.view.document, widgetUtils.BUTTON_PRESSED, self.on_document)
        if hasattr(self.view, "voice_message"):
            widgetUtils.connect_event(self.view.voice_message, widgetUtils.BUTTON_PRESSED, self.on_upload_voice_message)
        widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.on_remove_attachment)
        pub.subscribe(self.insert_attachment, self.modulename+"_insert_attachment")
        pub.subscribe(self.remove_attachment, self.modulename+"_remove_attachment")

    def uninstall(self):
        super(attachInteractor, self).uninstall()
        pub.unsubscribe(self.insert_attachment, self.modulename+"_insert_attachment")
        pub.unsubscribe(self.remove_attachment, self.modulename+"_remove_attachment")

    def on_image(self, *args, **kwargs):
        """ display menu for adding image attachments. """
        m = attachMenu()
        # disable add from VK as it is not supported in images, yet.
        m.add.Enable(False)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.on_upload_image, menuitem=m.upload)
        self.view.PopupMenu(m, self.view.photo.GetPosition())

    def on_audio(self, *args, **kwargs):
        """ display menu to add audio attachments."""
        m = attachMenu()
        widgetUtils.connect_event(m, widgetUtils.MENU, self.on_upload_audio, menuitem=m.upload)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.on_add_audio, menuitem=m.add)
        self.view.PopupMenu(m, self.view.audio.GetPosition())

    def on_document(self, *args, **kwargs):
        """ display menu for adding document attachments. """
        m = attachMenu()
        # disable add from VK as it is not supported in documents, yet.
        m.add.Enable(False)
        widgetUtils.connect_event(m, widgetUtils.MENU, self.on_upload_document, menuitem=m.upload)
        self.view.PopupMenu(m, self.view.photo.GetPosition())

    def on_upload_image(self, *args, **kwargs):
        """ allows uploading an image from the computer.
        """
        image, description  = self.view.get_image()
        if image != None:
            self.presenter.upload_image(image, description)

    def on_upload_audio(self, *args, **kwargs):
        """ Allows uploading an audio file from the computer. Only mp3 files are supported. """
        audio  = self.view.get_audio()
        if audio != None:
            self.presenter.upload_audio(audio)

    def on_upload_document(self, *args, **kwargs):
        """ allows uploading a document from the computer.
        """
        document  = self.view.get_document()
        if document != None:
            if document.endswith(".mp3") or document.endswith(".exe"):
                self.view.invalid_attachment()
                return
            self.presenter.upload_document(document)

    def on_upload_voice_message(self, *args, **kwargs):
        self.presenter.upload_voice_message()

    def on_add_audio(self, *args, **kwargs):
        """ Allow adding an audio directly from the user's audio library."""
        audios = self.presenter.get_available_audios()
        select = selector.selectAttachment(_("Select the audio files you want to send"), audios)
        if select.get_response() == widgetUtils.OK and select.attachments.GetCount() > 0:
            attachments = select.get_all_attachments()
            self.presenter.take_audios(attachments)

    def on_remove_attachment(self, *args, **kwargs):
        """ Remove the currently focused item from the attachments list."""
        current_item = self.view.attachments.get_selected()
        self.presenter.remove_attachment(current_item)
