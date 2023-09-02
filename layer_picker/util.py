
from krita import (
    Krita)

from PyQt5.QtCore import (
    QPointF)

from PyQt5.QtGui import (
    QTransform,
    QCursor)

from PyQt5.QtWidgets import *

# get_cursor_in_document_coords
# https://krita-artists.org/t/hot-to-get-the-mouse-position-in-a-plugin/41012/5


def __get_q_view(view):
    window = view.window()
    q_window = window.qwindow()
    q_stacked_widget = q_window.centralWidget()
    q_mdi_area = q_stacked_widget.findChild(QMdiArea)
    for v, q_mdi_view in zip(window.views(), q_mdi_area.subWindowList()):
        if v == view:
            return q_mdi_view.widget()


def __get_q_canvas(q_view):
    scroll_area = q_view.findChild(QAbstractScrollArea)
    viewport = scroll_area.viewport()
    for child in viewport.children():
        cls_name = child.metaObject().className()
        if cls_name.startswith('Kis') and ('Canvas' in cls_name):
            return child


def __get_transform(view):
    def _offset(scroller):
        mid = (scroller.minimum() + scroller.maximum()) / 2.0
        return -(scroller.value() - mid)
    canvas = view.canvas()
    document = view.document()
    q_view = __get_q_view(view)
    area = q_view.findChild(QAbstractScrollArea)
    zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
    transform = QTransform()
    transform.translate(
        _offset(area.horizontalScrollBar()),
        _offset(area.verticalScrollBar()))
    transform.rotate(canvas.rotation())
    if canvas.mirror():
        transform.scale(-zoom, zoom)
    else:
        transform.scale(zoom, zoom)
    return transform


def get_cursor_in_document_coords():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view.document():
        q_view = __get_q_view(view)
        q_canvas = __get_q_canvas(q_view)
        transform = __get_transform(view)
        transform_inv, _ = transform.inverted()
        global_pos = QCursor.pos()
        local_pos = q_canvas.mapFromGlobal(global_pos)
        center = q_canvas.rect().center()
        return transform_inv.map(local_pos - QPointF(center))

# getCurrentTool


def __searchCurrentTool(w):
    for c in w.children():
        if isinstance(c, QToolButton) and c.isChecked():
            return c.objectName()
        nm = __searchCurrentTool(c)
        if nm:
            return nm


def getCurrentTool():
    qdock = next((w for w in Krita.instance().dockers()
                 if w.objectName() == 'ToolBox'), None)
    if qdock is None:
        ValueError('ToolBox is not found. Please enable ToolBox docker.')
    return __searchCurrentTool(qdock)
