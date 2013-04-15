import sys

from PySide import QtGui
from PySide import QtCore

from obj_viewer.lib.pyside_dynamic import loadUi
from obj_viewer.constants import APP_NAME, EOL
from obj_viewer.errors import WrongFileFormatError
from obj_viewer.matrices import ViewportTransformation
from obj_viewer.model import Model


class Layout(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        super(Layout, self).__init__(*args, **kwargs)
        loadUi('obj_viewer/gui/layout.ui', self)
        self.current_file = None
        self.model = None
        self.connect_basic_controls()
        self.set_view()

    def connect_basic_controls(self):
        """Connect relevant signals to their slots."""
        # Main menu
        self.actionOpen.triggered.connect(self.choose_file)
        self.actionQuit.triggered.connect(QtCore.QCoreApplication.instance().quit)
        # Left panel (application controls)
        self.loadButton.clicked.connect(self.choose_file)
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        # Right panel (model transformation)
        self.reloadButton.clicked.connect(self.set_view)

    def connect_transformation_controls(self):
        if self.model is not None:
            self.actionReload.triggered.connect(self.model.reset)
            self.rotateXButton.clicked.connect(self.model.rotate_x)
            self.rotateYButton.clicked.connect(self.model.rotate_y)
            self.rotateZButton.clicked.connect(self.model.rotate_z)

    def choose_file(self):
        """Show a dialog that enables the user to choose a file
        to load, then set the view accordingly.
        """
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setNameFilter("Wavefront OBJ (*.obj)")
        if dialog.exec_():
            self.current_file = dialog.selectedFiles()[0]
            self.set_view(self.current_file)

    def set_view(self, filename = None):
        """Paint either a blank scene (if no filename has been
        specified) or the model stored in the file.
        """
        self.scene = QtGui.QGraphicsScene()
        if filename is None:
            filename = self.current_file
        if filename is not None:
            try:
                self.model = Model(self.scene,
                                   ViewportTransformation(),
                                   filename)
            except (IOError, WrongFileFormatError) as e:
                self.model = None
                sys.stderr.write(str(e) + EOL)
            self.update_controls()
            if self.model is not None:
                self.model.render()
                self.connect_transformation_controls()
        self.view.setScene(self.scene)
        self.view.show()

    def update_controls(self):
        # TODO: Not sure why this doesn't do anything...
        if self.current_file is not None:
            self.reloadButton.setEnabled(True)
            self.rotationBox.setEnabled(True)
            self.scalingBox.setEnabled(True)
            self.translationBox.setEnabled(True)
        else:
            self.reloadButton.setEnabled(False)
            self.rotationBox.setEnabled(False)
            self.scalingBox.setEnabled(False)
            self.translationBox.setEnabled(False)


def main():
    """Build the whole application."""
    application = QtGui.QApplication(sys.argv)
    layout = Layout()
    layout.show()
    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
