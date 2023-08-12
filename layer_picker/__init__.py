from krita import *

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.Qt import *
from .ExtensionModel import *

DOCKER_ID = "LayerPicker"

model=ExtensionModel()

class DockerTemplate(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_ID)
        ShadingWidget = QWidget()
        Layout = QHBoxLayout()
        self.StartShadingButton = QPushButton()
        self.onPicked()
        model.onPickedCallback=self.onPicked
        
        self.StartShadingButton.released.connect(
            lambda: model.beginCaptureMode()
        )
        self.StartShadingButton.released.connect(
            lambda: self.onButtonPress()
        )
        Layout.addWidget(self.StartShadingButton)
        ShadingWidget.setLayout(Layout)
        self.setWidget(ShadingWidget)

    def canvasChanged(self, canvas):
        pass

    def onButtonPress(self):
        self.StartShadingButton.setEnabled(False)
        self.StartShadingButton.setText("Please Touch Target Pixel...")

    def onPicked(self):
        self.StartShadingButton.setEnabled(True)
        self.StartShadingButton.setText("Pick Layer")

Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockRight, DockerTemplate))


class ExtensionTemplate(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(DOCKER_ID, DOCKER_ID)
        action.triggered.connect(model.run)

    def run():
        self.model.run()


Krita.instance().addExtension(ExtensionTemplate(Krita.instance()))
