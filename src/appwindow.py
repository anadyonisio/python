import gi
import numpy as np
import drawable
gi.require_version('Gtk', '3.0')
gi.require_foreign("cairo")

from enum import auto, Enum
from gi.repository import Gtk, Gdk
from transformations import rotation_matrix, viewport_matrix
from clipping import LineClippingMethod
from drawable import (
    Point,
    Vetor2D,
    Line,
    GraphicObject,
    Polygon,
    Rectangle,
    Window,
    View
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
    ARBITRARY = auto()

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
        name = entry_text(self, "name_entry")


        if OBJECT_TYPES[page_number] == "point":
            print("Ponto")
            x = float(entry_text(self, 'entry_x'))
            y = float(entry_text(self, 'entry_y'))
            self.dialog.new_object = Point(Vetor2D(x, y), name=name)

        elif OBJECT_TYPES[page_number] == "line":
            print("Reta")
            x1 = float(entry_text(self, 'entry_x1'))
            y1 = float(entry_text(self, 'entry_y1'))
            x2 = float(entry_text(self, 'entry_x2'))
            y2 = float(entry_text(self, 'entry_y2'))
            self.dialog.new_object = Line(Vetor2D(x1, y1), Vetor2D(x2, y2), name=name)

        elif OBJECT_TYPES[page_number] == "polygon":
            print("Polígono")
            if len(self.vertices) >= 3:
                filled = self.builder.get_object('switch_filled').get_active()
                self.dialog.new_object = Polygon(self.vertices, name=name, filled=filled )
        else:
            print("Invalid Page")
            raise ValueError('No page with given index.')
        window.destroy()

    def onAddPoint(self, widget):
        x = float(entry_text(self, 'entry_x3'))
        y = float(entry_text(self, 'entry_y3'))
        self.vertices.append(Vetor2D(x, y))

        print(f'Ponto Adicionado: {x}, {y}')


class NewObjectWindow(Gtk.Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

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
        self.view = View()
        self.world_win = None
        self.press_start = None
        self.size = []
        self.rotation_ref = RotationRef.CENTER
        self.clipping_method = LineClippingMethod.COHEN_SUTHERLAND

    def onDestroy(self, *args):
        self.window.get_application().quit()

    def viewport(self) -> Rectangle:
        widget = self.builder.get_object('drawing_area')
        return Rectangle(
            min=Vetor2D(0, 0),
            max=Vetor2D(
                widget.get_allocated_width(),
                widget.get_allocated_height(),
            )
        ).with_margin(10)

    def onDraw(self, widget, cr):
        if self.view.window is None:
            self.size = (widget.get_allocated_width(), widget.get_allocated_height())
            self.view.window = Window(
                Vetor2D(-self.size[0]/2,-self.size[1]/2),
                Vetor2D(self.size[0]/2, self.size[1]/2),
            )

        viewport = self.viewport()
        vp_matrix = viewport_matrix(viewport)

        cr.set_line_width(1.0)
        cr.paint()
        cr.set_source_rgb(0, 0, 100)

        for object in self.view.obj_list:
            clipped = object.clipped(method=self.clipping_method)
            if clipped:
                clipped.draw(cr, vp_matrix)
        viewport.draw(cr, vp_matrix)

    def onNewObject(self, widget):
        dialog = NewObjectWindow()
        response = dialog.dialog_window.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            if dialog.new_object is not None:
                self.view.add_object(dialog.new_object)
                self.add_object(dialog.new_object)
                self.builder.get_object("drawing_area").queue_draw()
            else:
                print("Objeto Inválido")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

    def add_object(self, object: GraphicObject):
        self.object_store.append([object.name, str(f'{type(object).__name__}')])

    def onResize(self, widget: Gtk.Widget, allocation: Gdk.Rectangle):
        w_proportion = allocation.width / self.size[0]
        h_proportion = allocation.height / self.size[1]

        self.view.window.max = Vetor2D(
            self.view.window.max.x * w_proportion,
            self.view.window.max.y * h_proportion
        )
        self.view.window.min = Vetor2D(
            self.view.window.min.x * w_proportion,
            self.view.window.min.y * h_proportion
        )

        self.size = (allocation.width, allocation.height)
        self.view.update_norm_coord()

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
                        args[0] @ rotation_matrix(self.view.window.angle)
                )
                object.translate(*args)
            elif op == 'scale':
                object.scale(*args)
            elif op == 'rotate':
                try:
                    arb_x = int(entry_text(self, 'rot_x'))
                    arb_y = int(entry_text(self, 'rot_y'))
                except ValueError:
                    arb_x = 0
                    arb_y = 0

                ref = {
                    RotationRef.CENTER: object.centroid,
                    RotationRef.ORIGIN: Vetor2D(0, 0),
                    RotationRef.ARBITRARY: Vetor2D(float(arb_x), float(arb_y)),
                }[self.rotation_ref]

                object.rotate(*args, ref)
            object.update_norm_coord(self.view.window)

        self.window.queue_draw()

    def selected_objs(self):
        tree = self.builder.get_object('tree_displayfiles')
        store, rows = tree.get_selection().get_selected_rows()

        return (self.view.obj_list[int(str(index))] for index in rows)

    def on_rotation_ref(self, widget: Gtk.RadioButton):
        for w in widget.get_group():
            if w.get_active():
                self.rotation_ref = {
                    'rotate-obj-center': RotationRef.CENTER,
                    'rotate-origin': RotationRef.ORIGIN,
                    'rotate-arb': RotationRef.ARBITRARY,
                }[w.get_name()]
                if w.get_name() == 'rotate-arb':
                    for _id in 'rot_x', 'rot_y':
                        self.builder.get_object(_id).set_editable(True)

    def onRotationWindow(self, widget: Gtk.Button):
        rotation_angle = int(entry_text(self, 'rot_window_entry'))
        self.view.window.angle += rotation_angle
        for object in self.view.obj_list:
            object.update_norm_coord(self.view.window)
        self.window.queue_draw()

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        builder = Gtk.Builder()
        builder.add_from_file("../interface/main_window.glade")

        self.window = builder.get_object("main_window")

        builder.connect_signals(MainWindowHandler(builder))
