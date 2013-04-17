import sys

from PySide import QtGui
from PySide import QtCore

from obj_viewer.lib.pyside_dynamic import loadUi
from obj_viewer.constants import APP_NAME, EOL, DEGREES, TRANSL_DIST
from obj_viewer.errors import WrongFileFormatError
from obj_viewer.matrices import Rotation, Translation, Scaling
from obj_viewer.model import Model


class Layout(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        super(Layout, self).__init__(*args, **kwargs)
        loadUi('obj_viewer/gui/layout.ui', self)
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
        self.actionReload.triggered.connect(self.transformation_clicked)
        # Left panel (application controls)
        self.loadButton.clicked.connect(self.choose_file)
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        # Right panel (model transformation)
        self.reloadButton.clicked.connect(self.transformation_clicked)
        self.rotateXButton.clicked.connect(self.transformation_clicked)
        self.rotateYButton.clicked.connect(self.transformation_clicked)
        self.rotateZButton.clicked.connect(self.transformation_clicked)
        self.translateXButton.clicked.connect(self.transformation_clicked)
        self.translateYButton.clicked.connect(self.transformation_clicked)
        self.translateZButton.clicked.connect(self.transformation_clicked)
        self.scaleUpButton.clicked.connect(self.transformation_clicked)
        self.scaleDownButton.clicked.connect(self.transformation_clicked)

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
                sys.stderr.write(str(e) + EOL)
            if self.model is not None:
                # TODO: look into the scene's autocentering
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

    def transformation_clicked(self):
        # TODO: replace this dummy method with something nicer
        sender = self.sender().objectName()
        if sender.startswith('reload'):
            self.model.reset()
        elif sender.startswith('rotate'):
            self.model.transform(Rotation(sender[6].lower(), degrees = DEGREES))
        elif sender.startswith('translate'):
            self.model.transform(Translation(sender[9].lower(), TRANSL_DIST))
        elif sender == 'scaleUpButton':
            self.model.transform(Scaling(1.1))
        elif sender == 'scaleDownButton':
            self.model.transform(Scaling(0.9))
        self.update_matrix()

    # TODO: this should really be tablewidget's method
    def update_matrix(self):
        for r, row in enumerate(self.model.current_mod):
            for c, col in enumerate(row):
                self.matrixView.setItem(r, c, QtGui.QTableWidgetItem('%.3f' % col))

def main():
    """Build the whole application."""
    application = QtGui.QApplication(sys.argv)
    layout = Layout()
    layout.show()
    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
