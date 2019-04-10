import gi
import numpy as np
gi.require_version('Gtk', '3.0')
gi.require_foreign("cairo")
from gi.repository import Gtk
from drawable import Point, Vetor2D, Line, GraphicObject #, Polygon

object_types = {
    0: "point",
    1: "line",
    2: "polygon"
    }

class NewObjectWindowHandler:
    def __init__(self, dialog, builder):
        self.dialog = dialog
        self.builder = builder
        self.pontos = []

    def onCancel(self, widget):
        dialog = self.builder.get_object("dialog_object")
        dialog.destroy()

    def onOK(self, widget):
        window = self.builder.get_object("dialog_window")
        notebook = self.builder.get_object("notebook1")

        page_number = notebook.get_current_page()
        name = self.builder.get_object("name_entry").get_text()

        if object_types[page_number] == "point":
            print("Ponto")
            x = float(self.builder.get_object('entry_x').get_text())
            y = float(self.builder.get_object('entry_y').get_text())
            self.dialog.new_object = Point(Vetor2D(x, y), name=name)

        elif object_types[page_number] == "line":
            print("Reta")
            x1 = float(self.builder.get_object('entry_x1').get_text())
            y1 = float(self.builder.get_object('entry_y1').get_text())
            x2 = float(self.builder.get_object('entry_x2').get_text())
            y2 = float(self.builder.get_object('entry_y2').get_text())
            self.dialog.new_object = Line(Vetor2D(x1, y1), Vetor2D(x2, y2), name=name)

        elif object_types[page_number] == "polygon":
            print("Polígono")
            # if len(self.pontos) >= 3:
            #     self.dialog.new_object = Polygon(self.pontos, name=name)
        else:
            print("Invalid Page")
        window.destroy()

    def onAddPoint(self, widget):
        print("Ponto Adcionado")



class NewObjectWindow(Gtk.Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        #self.set_default_size(150, 100)

        self.builder = Gtk.Builder.new_from_file("../interface/dialog_object.glade")
        self.builder.connect_signals(
            NewObjectWindowHandler(self, self.builder)
        )
        self.new_object = None

        self.dialog_window = self.builder.get_object("dialog_object")

class MainWindowHandler:
    def __init__(self, builder):
        self.builder = builder
        self.window = self.builder.get_object("main_window")
        self.object_store = self.builder.get_object("object_store")
        self.display_file = []

    def onDestroy(self, *args):
        self.window.get_application().quit()

    def onDraw(self, widget, cr):
        cr.set_line_width(1.0)
        cr.set_source_rgb(0, 0, 0)
        for object in self.display_file:
            if object:
                object.draw(cr)
        cr.stroke()

    def onNewObject(self, widget):
        dialog = NewObjectWindow()
        response = dialog.dialog_window.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            self.add_object(dialog.new_object)
            self.builder.get_object("drawing_area").queue_draw()

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")


    def add_object(self, object: GraphicObject):
        self.display_file.append(object)
        self.object_store.append([object.name,
            str(f'{type(object).__name__}')])

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        builder = Gtk.Builder()
        builder.add_from_file("../interface/main_window.glade")

        self.window = builder.get_object("main_window")

        builder.connect_signals(MainWindowHandler(builder))