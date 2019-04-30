import gi
import numpy as np
import drawable
gi.require_version('Gtk', '3.0')
gi.require_foreign("cairo")

from enum import auto, Enum
from gi.repository import Gtk, Gdk
from transformations import rotation_matrix
from drawable import (
    Point,
    Vetor2D,
    Line,
    GraphicObject,
    Polygon,
    Rectangle,
    Viewport,
    Window,
)

OBJECT_TYPES = {
    0: "point",
    1: "line",
    2: "polygon"
    }

EVENTS = {
    1: 'left',
    2: 'middle',
    3: 'right',
}

def entry_text(handler, entry_id: str) -> str:
    return handler.builder.get_object(entry_id).get_text()

class RotationRef(Enum):
    CENTER = auto()
    ORIGIN = auto()
    ABSOLUTE = auto()

class NewObjectWindowHandler:
    def __init__(self, dialog, builder):
        self.dialog = dialog
        self.builder = builder
        self.vertices = []

    def onCancel(self, widget):
        dialog = self.builder.get_object("dialog_object")
        dialog.destroy()

    def onOk(self, widget):
        window = self.builder.get_object("dialog_object")
        notebook = self.builder.get_object("notebook1")

        page_number = notebook.get_current_page()
        name = self.builder.get_object("name_entry").get_text()


        if OBJECT_TYPES[page_number] == "point":
            print("Ponto")
            x = float(self.builder.get_object('entry_x').get_text())
            y = float(self.builder.get_object('entry_y').get_text())
            self.dialog.new_object = Point(Vetor2D(x, y), name=name)

        elif OBJECT_TYPES[page_number] == "line":
            print("Reta")
            x1 = float(self.builder.get_object('entry_x1').get_text())
            y1 = float(self.builder.get_object('entry_y1').get_text())
            x2 = float(self.builder.get_object('entry_x2').get_text())
            y2 = float(self.builder.get_object('entry_y2').get_text())
            self.dialog.new_object = Line(Vetor2D(x1, y1), Vetor2D(x2, y2), name=name)

        elif OBJECT_TYPES[page_number] == "polygon":
            print("Polígono")
            if len(self.vertices) >= 3:
                 self.dialog.new_object = Polygon(self.vertices, name=name)
        else:
            print("Invalid Page")
            raise ValueError('No page with given index.')
        window.destroy()

    def onAddPoint(self, widget):
        x = float(self.builder.get_object('entry_x3').get_text())
        y = float(self.builder.get_object('entry_y3').get_text())
        self.vertices.append(Vetor2D(x, y))

        print("Ponto Adicionado")

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
        self.world_win = None
        self.press_start = None
        self.size = []
        self.rotation_ref = RotationRef.CENTER

    def onDestroy(self, *args):
        self.window.get_application().quit()

    def viewport(self) -> drawable.Viewport:
        widget = self.builder.get_object('drawing_area')
        return drawable.Viewport(
            region=Rectangle(
                min=Vetor2D(0, 0),
                max=Vetor2D(
                    widget.get_allocated_width(),
                    widget.get_allocated_height(),
                ),
            ).with_margin(10),
            window=self.world_win,
        )

    def onDraw(self, widget, cr):
        if self.world_win is None:
            self.size = (widget.get_allocated_width(), widget.get_allocated_height())
            self.world_win = Window(
                Vetor2D(-self.size[0]/2,- self.size[1]/2),
                Vetor2D(self.size[0]/2, self.size[1])/2,
            )

        def win_to_vp(v: Vetor2D):
            window = self.world_win
            vp_min = viewport.region.min
            width_vp = viewport.width
            height_vp = viewport.height

            return Vetor2D( vp_min.x +(v.x - window.min.x)/window.width * width_vp,
                           vp_min.y +(1-((v.y - window.min.y)/window.height)) * height_vp)

        viewport = self.viewport()
        cr.set_line_width(1.0)
        cr.paint()
        cr.set_source_rgb(0, 0, 0)

        for object in self.display_file:
            if object:
                object.draw(cr,viewport, win_to_vp)
        viewport.draw(cr)

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
        # window = self.world_win or Rectangle(Vetor2D(-1, -1), Vetor2D(1, 1))
        #
        # object.normalize(window)
        self.display_file.append(object)
        self.object_store.append([object.name,
           str(f'{type(object).__name__}')])

    def onResize(self, widget: Gtk.Widget, allocation: Gdk.Rectangle):
        w_proportion = allocation.width / self.size[0]
        h_proportion = allocation.height / self.size[1]

        self.world_win.max = Vetor2D(
            self.world_win.max.x * w_proportion,
            self.world_win.max.y * h_proportion
        )
        self.world_win.min = Vetor2D(
            self.world_win.min.x * w_proportion,
            self.world_win.min.y * h_proportion
        )

        self.size = (allocation.width, allocation.height)

    def navigationButton(self, widget):
        TRANSFORMATIONS = {
            'nav-move-up': ('translate', Vetor2D(0, 10)),
            'nav-move-down': ('translate', Vetor2D(0, -10)),
            'nav-move-left': ('translate', Vetor2D(-10, 0)),
            'nav-move-right': ('translate', Vetor2D(10, 0)),
            'nav-rotate-left': ('rotate', -5),
            'nav-rotate-right': ('rotate', 5),
            'nav-zoom-in': ('scale', Vetor2D(1.1, 1.1)),
            'nav-zoom-out': ('scale', Vetor2D(0.9, 0.9)),
        }

        op, *args = TRANSFORMATIONS[widget.get_name()]

        for object in self.selected_objs():
            if op == 'translate':
                args[0] = (
                        args[0] @
                        rotation_matrix(self.world_win.angle)
                )
                object.translate(*args)
            elif op == 'scale':
                object.scale(*args)

            # Not working
            elif op == 'rotate':
                try:
                    abs_x = int(entry_text(self, 'rot_x'))
                    abs_y = int(entry_text(self, 'rot_y'))
                except ValueError:
                    abs_x = 0
                    abs_y = 0

                ref = {
                    RotationRef.CENTER: object.centroid,
                    RotationRef.ORIGIN: Vetor2D(0, 0),
                    RotationRef.ABSOLUTE: Vetor2D(float(abs_x), float(abs_y)),
                }[self.rotation_ref]

                object.rotate(*args, ref)
            object.normalize(self.world_win)

        self.window.queue_draw()

    def selected_objs(self):
        tree = self.builder.get_object('tree_displayfiles')
        store, rows = tree.get_selection().get_selected_rows()

        return (self.display_file[int(str(index))] for index in rows)


    ############ Not working
    def onButtonPress(self, widget, event):
        if EVENTS[event.button] == 'left':
            self.press_start = Vetor2D(-event.x, event.y)
            self.dragging = True

    def onButtonRelease(self, widget, event):
        if EVENTS[event.button] == 'left':
            self.dragging = False

    def onMotion(self, widget, event):
        def vp_to_win(v: Vetor2D):
            viewport = self.viewport()

            return Vetor2D(
                (v.x / viewport.width) * self.world_win.width,
                (v.y / viewport.height) * self.world_win.height
            )

        if self.dragging:
            current = Vetor2D(-event.x, event.y)
            delta = vp_to_win(current - self.press_start)
            self.press_start = current
            self.world_win.min += delta
            self.world_win.max += delta
            widget.queue_draw()
    ###########################

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        builder = Gtk.Builder()
        builder.add_from_file("../interface/main_window.glade")

        self.window = builder.get_object("main_window")

        builder.connect_signals(MainWindowHandler(builder))
