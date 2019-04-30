# Created by Ana Cristina Medaglia Dyonisio

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_foreign("cairo")
from appwindow import AppWindow

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None

    def do_startup(self):
        # Initialize Gtk.Application Framework
        Gtk.Application.do_startup(self)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            app_window = AppWindow(application=self, title="Sistema Básico")
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = app_window.window
            self.window.set_application(self)
        self.window.present()

    """
    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0
    

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()
    
    """

if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)


