from krita import *

from PyQt5.QtCore import (
    QPointF,
    Qt,
    pyqtSignal as QSignal,
    QObject,
    QEvent,
    QCoreApplication
)

from .util import *

from PyQt5.QtWidgets import (
        QToolTip,)

class Hook(QObject):
    _target_key = Qt.Key_F10

    mouse_press = QSignal(bool)
    mouse_move = QSignal(bool)

    def eventFilter(self, obj, e):
        e_type = e.type()
        if (e_type == QEvent.MouseButtonPress):
            self.mouse_press.emit(False)
            return False
        if (e_type == QEvent.MouseButtonRelease):
            self.mouse_press.emit(True)
            return False
        # if (e_type == QEvent.MouseMove):
        #     self.mouse_move.emit(False)
        #     return False
        return super().eventFilter(obj, e)


class ExtensionModel():
    onPickedCallback = None
    pickPos = QPointF()

    def __init__(self):
        pass

    def setup(self):
        pass

    def onMousePress(self, is_release):
        if is_release:
            self.run()
            self.app.removeEventFilter(self.hook)
            self.is_dragging = False
            if self.onPickedCallback:
                self.onPickedCallback()
        else:
            self.is_dragging = True

    # def onMouseMove(self, is_release):
    #     pass

    def beginCaptureMode(self):
        # inst = Krita.instance()
        # view = inst.activeWindow().activeView()
        # self.lastForgroundColor = view.foregroundColor()
        self.lastToolName = getCurrentTool()  # backup tool
        Krita.instance().action('KritaSelected/KisToolColorSampler').trigger()
        self.lastColorSamplerSources = getColorSamplerSources()  # backup ColorSamplerSources
        setColorSamplerSources(0)  # set all layer source
        self.lastColorSamplerRadius = getColorSamplerRadius()  # backup ColorSamplerRadius
        setColorSamplerRadius(1)  # set Radius

        self.hook = Hook()
        self.app = QCoreApplication.instance()

        self.app.installEventFilter(self.hook)
        self.is_dragging = False

        self.hook.mouse_press.connect(self.onMousePress)
        # self.hook.mouse_move.connect(self.onMouseMove)

    def run(self):
        inst = Krita.instance()
        view = inst.activeWindow().activeView()
        doc = view.document()
        if doc:
            self.pickPos = get_cursor_in_document_coords()
            self.foundNode = None
            self.checkRecursive(doc.topLevelNodes(), self.pickPos)
            if self.foundNode:
                doc.setActiveNode(self.foundNode)
            if self.lastToolName:
                setColorSamplerSources(
                    self.lastColorSamplerSources)  # restore setting
                setColorSamplerRadius(self.lastColorSamplerRadius)
                Krita.instance().action(self.lastToolName).trigger()  # restore tool
            # view.setForeGroundColor(self.lastForgroundColor)

    def checkRecursive(self, nodes, pos):
        for child in reversed(nodes):
            if child.opacity() > 0 and child.visible():
                if child.type() == 'paintlayer' or child.type() == 'vectorlayer':
                    # TODO:vectorLayerのピクセルデータ参照の仕方がわからない
                    color = child.pixelData(pos.x(), pos.y(), 1, 1)
                    if color:
                        (b, g, r, a) = color
                        if int.from_bytes(a, sys.byteorder) > 0:
                            self.foundNode = child
                            return True
                if self.checkRecursive(child.childNodes(), pos):
                    return True
        return False
