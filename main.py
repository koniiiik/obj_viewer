import sys

from PySide import QtGui
from PySide import QtCore

from obj_viewer.lib import pyside_dynamic
from obj_viewer.constants import EOL, FACTOR_PLUS, FACTOR_MINUS
from obj_viewer.errors import WrongFileFormatError
from obj_viewer.matrices import Rotation, Translation, Scaling
from obj_viewer.model import Model


class Layout(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        super(Layout, self).__init__(*args, **kwargs)
        pyside_dynamic.loadUi('obj_viewer/gui/layout.ui', self)
        # TODO: do we really need to remember the current file?
        self.current_file = None
        self.model = None
        self.update_transform_controls()
        self.connect_controls()
        self.set_view()

    def connect_controls(self):
        """Connect relevant signals to their slots."""
        # Main menu
        self.actionOpen.triggered.connect(self.choose_file)
        self.actionQuit.triggered.connect(QtCore.QCoreApplication.instance().quit)
        self.actionReload.triggered.connect(self.reload_clicked)
        # Left panel (application controls)
        self.loadButton.clicked.connect(self.choose_file)
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        # Right panel (model transformation)
        self.reloadButton.clicked.connect(self.reload_clicked)
        self.rotateXButton.clicked.connect(self.transformation_clicked(rotate = {'axis': 'x'}))
        self.rotateYButton.clicked.connect(self.transformation_clicked(rotate = {'axis': 'y'}))
        self.rotateZButton.clicked.connect(self.transformation_clicked(rotate = {'axis': 'z'}))
        self.translateXButton.clicked.connect(self.transformation_clicked(translate = {'axis': 'x'}))
        self.translateYButton.clicked.connect(self.transformation_clicked(translate = {'axis': 'y'}))
        self.translateZButton.clicked.connect(self.transformation_clicked(translate = {'axis': 'z'}))
        self.scaleUpButton.clicked.connect(self.transformation_clicked(scale = {'factor': FACTOR_PLUS}))
        self.scaleDownButton.clicked.connect(self.transformation_clicked(scale = {'factor': FACTOR_MINUS}))

    def set_view(self, filename = None):
        """Paint either a blank scene (if no filename has been
        specified) or the model stored in the file.
        """
        self.scene = QtGui.QGraphicsScene()
        if filename is None:
            filename = self.current_file
        if filename is not None:
            try:
                self.model = Model(self.scene, filename)
            except (IOError, WrongFileFormatError) as e:
                self.model = None
                err = QtGui.QMessageBox(self)
                err.setWindowTitle('Oops!')
                err.setText(str(e))
                err.exec()
                sys.stderr.write(str(e) + EOL)
            if self.model is not None:
                # TODO: look into the scene's autocentering
                # and/or autoresizing
                self.model.render()
                self.update_matrix()
        self.update_transform_controls()
        self.view.setScene(self.scene)
        self.view.show()

    def update_transform_controls(self):
        """Either enable or disable the model transformation controls
        (e.g. the rotation buttons) based on whether there's a model
        to apply them to.
        """
        if self.model is not None:
            self.reloadButton.setEnabled(True)
            self.rotationBox.setEnabled(True)
            self.scalingBox.setEnabled(True)
            self.translationBox.setEnabled(True)
        else:
            self.reloadButton.setEnabled(False)
            self.rotationBox.setEnabled(False)
            self.scalingBox.setEnabled(False)
            self.translationBox.setEnabled(False)

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

    def reload_clicked(self):
        self.model.reset()
        self.update_matrix()

    def transformation_clicked(self, rotate = None,
                               translate = None, scale = None):
        if rotate is not None:
            matrix = Rotation(**rotate)
        elif translate is not None:
            matrix = Translation(**translate)
        elif scale is not None:
            matrix = Scaling(**scale)
        def transform():
            self.model.transform(matrix)
            self.update_matrix()
        return transform

    # TODO: consider subclassing QTableWidget later
    def update_matrix(self):
        for r, row in enumerate(self.model.current_mod):
            for c, num in enumerate(row):
                if int(num) == num:
                    self.matrixView.setItem(r, c,
                                            QtGui.QTableWidgetItem(str(int(num))))
                else:
                    self.matrixView.setItem(r, c,
                                            QtGui.QTableWidgetItem('%.3f' % num))

def main():
    """Build the whole application."""
    application = QtGui.QApplication(sys.argv)
    layout = Layout()
    layout.show()
    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
