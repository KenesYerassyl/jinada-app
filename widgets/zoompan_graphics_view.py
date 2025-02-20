from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QPainter, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt, QPoint, QPointF


class ZoomPanGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.zoom_factor = 1.05
        self.pan_speed = 1
        self.min_zoom = 0.3
        self.max_zoom = 7.0
        self.current_zoom = 0.5
        self.scale(0.5, 0.5)
        # 0 - for regular mode
        # 1 - for panning mode
        self.cursor_mode = 0
        self.last_pan_point = None

    def set_cursor_mode(self, mode):
        self.cursor_mode = mode
        if mode == 1:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        cursor_scene_pos = self.mapToScene(event.position().toPoint())
        zoom_in = event.angleDelta().y() > 0
        scale_factor = self.zoom_factor if zoom_in else 1 / self.zoom_factor
        if (zoom_in and self.current_zoom < self.max_zoom) or (
            not zoom_in and self.current_zoom > self.min_zoom
        ):
            self.current_zoom = (
                self.current_zoom * self.zoom_factor
                if zoom_in
                else self.current_zoom / self.zoom_factor
            )
            self.scale(scale_factor, scale_factor)

            new_cursor_scene_pos = self.mapToScene(event.position().toPoint())
            delta = new_cursor_scene_pos - cursor_scene_pos
            self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: QMouseEvent):
        if self.cursor_mode == 1 and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_pan_point = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.cursor_mode == 1 and self.last_pan_point is not None:
            current_pos = self.mapToScene(event.pos())
            last_pos = self.mapToScene(self.last_pan_point)
            delta = current_pos - last_pos
            self.pan(delta)
            self.last_pan_point = event.pos()
        else:
            super().mouseMoveEvent(event)

    def pan(self, delta: QPointF):
        delta *= self.current_zoom
        delta *= self.pan_speed

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        new_center = QPoint(
            int(self.viewport().rect().width() * 0.5 - delta.x()),
            int(self.viewport().rect().height() * 0.5 - delta.y()),
        )
        self.centerOn(self.mapToScene(new_center))
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def mouseReleaseEvent(self, event):
        if self.cursor_mode == 1 and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.last_pan_point = None
        else:
            super().mouseReleaseEvent(event)
