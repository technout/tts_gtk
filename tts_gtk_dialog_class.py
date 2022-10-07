import time
from gi.repository import Gtk, GLib

class DialogWindow(Gtk.Window): # test
    def __init__(self):
        super().__init__(title="FileChooser Example")

        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button(label="Choose File")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

        button2 = Gtk.Button(label="Choose Folder")
        button2.connect("clicked", self.on_folder_clicked)
        box.add(button2)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


# win = FileChooserWindow()
# win.connect("destroy", Gtk.main_quit)
# win.show_all()
# Gtk.main()

# todo: make class object
def on_save_clicked(): # Error todo: Gtk-CRITICAL: gtk_file_chooser_get_files: assertion 'GTK_IS_FILE_CHOOSER (chooser)' failed
    win = DialogWindow()
    # dialog = Gtk.FileChooserDialog(title="Save your audio file:",
    #     parent=None, action=Gtk.FileChooserAction.SAVE)
    # dialog.add_buttons(
    #     Gtk.STOCK_CANCEL,
    #     Gtk.ResponseType.CANCEL,
    #     Gtk.STOCK_SAVE,
    #     Gtk.ResponseType.OK,
    # )

    # # dialog.add_filters(dialog)
    # filter_text = Gtk.FileFilter()
    # filter_text.set_name("Wav files")
    # filter_text.add_mime_type("audio/wav")
    # dialog.add_filter(filter_text)

    # filter_any = Gtk.FileFilter()
    # filter_any.set_name("Any files")
    # filter_any.add_pattern("*")
    # dialog.add_filter(filter_any)
    # dialog.set_current_name(f'tts_export_{random.randrange(100,999)}.wav')
    # dialog.set_do_overwrite_confirmation(True)

    # response = dialog.run()
    # if response == Gtk.ResponseType.OK:
    #     print("Save clicked")
    #     print("File selected: " + dialog.get_filename())
    #     dialog.destroy()
    #     return dialog.get_filename()
    # # elif response == Gtk.ResponseType.CANCEL:
    # else:
    #     print("Cancel clicked")
    #     dialog.destroy()
    #     return None

class update_TimeLabel_Test(Gtk.Label): # todo: remove from code
    def __init__(self):
        Gtk.Label.__init__(self, "")
        GLib.timeout_add_seconds(1, self.updateTime)
        self.updateTime()

    def updateTime(self):
        timeStr = self.getTime()
        self.set_text(timeStr)
        return GLib.SOURCE_CONTINUE

    def getTime(self):
        return time.strftime("%c")