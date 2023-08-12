from krita import *

from PyQt5.QtCore import (
    QPointF,
    Qt,
    pyqtSignal as QSignal,
    QObject,
    QEvent,
    QCoreApplication
)

from .util import get_cursor_in_document_coords

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
    onPickedCallback=None

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
        Krita.instance().action('KritaSelected/KisToolColorSampler').trigger()
        self.hook = Hook()
        self.app = QCoreApplication.instance()

        self.app.installEventFilter(self.hook)
        self.is_dragging = False

        self.hook.mouse_press.connect(self.onMousePress)
        #self.hook.mouse_move.connect(self.onMouseMove)

    def run(self):
        inst = Krita.instance()
        view = inst.activeWindow().activeView()
        doc = view.document()
        if doc:
            center = QPointF(0.5 * doc.width(), 0.5 * doc.height())
            p = get_cursor_in_document_coords()
            doc_pos = p + center
            self.foundNode = None
            self.checkRecursive(doc.topLevelNodes(), doc_pos)
            if self.foundNode:
                doc.setActiveNode(self.foundNode)

    def checkRecursive(self, nodes, pos):
        for child in reversed(nodes):
            if child.opacity() > 0 and child.visible():
                if child.type() == 'paintlayer' or child.type() == 'vectorlayer':
                    #TODO:vectorLayerのピクセルデータ参照の仕方がわからない
                    color = child.pixelData(pos.x(), pos.y(), 1, 1)
                    if color:
                        (b, g, r, a) = color
                        if int.from_bytes(a, sys.byteorder) > 0:
                            self.foundNode = child
                            return True
                if self.checkRecursive(child.childNodes(), pos):
                    return True
        return False