import sys

from PySide import QtGui
from PySide import QtCore
from obj_viewer.lib.pyside_dynamic import loadUi

from obj_viewer.errors import WrongFileFormatError
from obj_viewer.matrices import ViewportTransformation
from obj_viewer.model import Model


VIEW_MATRIX = ViewportTransformation()


class Scene(QtGui.QGraphicsScene):

    def populate(self, model = None):
        """If a model has been specified, transform it using
        VIEW_MATRIX and create the scene.
        """
        if model is not None:
            for face in model.faces:
                for i, vertex in enumerate(face):
                    x1, y1, z1 =\
                        model.vertices[vertex].get_viewport_coordinates(VIEW_MATRIX)
                    x2, y2, z2 =\
                        model.vertices[face.get_next_vertex(i)].get_viewport_coordinates(VIEW_MATRIX)
                    self.addLine(x1, y1, x2, y2)


class Layout(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        super(Layout, self).__init__(*args, **kwargs)
        loadUi('obj_viewer/gui/layout.ui', self)
        self.connect_actions()
        self.set_view()

    def connect_actions(self):
        """Connect relevant signals to their slots."""
        self.loadButton.clicked.connect(self.choose_file)
        self.actionOpen.triggered.connect(self.choose_file)
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.actionQuit.triggered.connect(QtCore.QCoreApplication.instance().quit)

    def choose_file(self):
        """Show a dialog that enables the user to choose a file
        to load, then set the view accordingly.
        """
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setNameFilter("Wavefront OBJ (*.obj)")
        if dialog.exec_():
            self.set_view(dialog.selectedFiles()[0])

    def set_view(self, filename = None):
        """Paint either a blank scene (if no filename has been
        specified) or the model stored in the file.
        """
        self.scene = Scene()
        if filename is not None:
            try:
                model = Model(filename)
            except (IOError, WrongFileFormatError) as e:
                model = None
                sys.stderr.write(str(e) + EOL)
            self.scene.populate(model)
        self.view.setScene(self.scene)
        self.view.show()


def main():
    """Build the whole application."""
    application = QtGui.QApplication(sys.argv)
    layout = Layout()
    layout.show()
    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
