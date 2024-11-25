from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QWidget,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QGraphicsPixmapItem,
    QToolButton,
    QGraphicsItemGroup,
)
from PyQt6.QtGui import (
    QPixmap,
    QPen,
    QBrush,
    QPainter,
    QIcon,
    QWheelEvent,
    QMouseEvent,
    QKeyEvent,
)
from PyQt6.QtCore import Qt, QEvent, QRectF, QPoint, QPointF
from utils.object import Object


class ObjectModifierDialog(QDialog):
    def __init__(self, object: Object, parent=None):
        super().__init__(parent)
        self.object = object
        self.setWindowTitle("Object modification")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        layout = QVBoxLayout(self)

        # input text
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name_label.setText(f"Name of the object: {self.object.get_name()}")
        # initial frame graphics scene
        self.polygon_drawer = PolygonDrawer(object.get_frame_path())
        # buttons
        self.upload_button = QPushButton("Upload")
        self.back_button = QPushButton("Back")
        self.upload_button.clicked.connect(self.on_upload)
        self.back_button.clicked.connect(self.on_back)

        self.button_box = QDialogButtonBox(self)
        self.button_box.addButton(
            self.upload_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.button_box.addButton(
            self.back_button, QDialogButtonBox.ButtonRole.RejectRole
        )

        layout.addWidget(self.name_label)
        layout.addWidget(self.polygon_drawer)
        layout.addWidget(self.button_box)

    def on_upload(self):
        self.accept()

    def on_back(self):
        self.reject()


class PolygonDrawer(QWidget):
    def __init__(self, frame_path):
        super().__init__()

        self.layout = QVBoxLayout()
        self.scene = QGraphicsScene()
        self.view = ZoomPanGraphicsView(self.scene)

        self.pan_mode_button = QToolButton()
        self.pan_mode_button.setIcon(QIcon("./resources/icons/move.svg"))
        self.pan_mode_button.setCheckable(True)
        self.pan_mode_button.toggled.connect(self.activate_pan_mode)

        self.confirm_polygon_button = QToolButton()
        self.confirm_polygon_button.setIcon(QIcon("./resources/icons/confirm.svg"))
        self.confirm_polygon_button.setVisible(False)
        self.confirm_polygon_button.clicked.connect(self.confirm_polygon)

        self.reject_polygon_button = QToolButton()
        self.reject_polygon_button.setIcon(QIcon("./resources/icons/reject.svg"))
        self.reject_polygon_button.setVisible(False)
        self.reject_polygon_button.clicked.connect(self.reject_polygon)

        self.in_frame_button = QPushButton("Add in-frame")
        self.in_frame_button.clicked.connect(self.activate_in_frame_drawing)

        self.out_frame_button = QPushButton("Add out-frame")
        self.out_frame_button.clicked.connect(self.activate_out_frame_drawing)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.pan_mode_button)
        self.buttons_layout.addWidget(self.in_frame_button)
        self.buttons_layout.addWidget(self.out_frame_button)
        self.buttons_layout.addWidget(self.confirm_polygon_button)
        self.buttons_layout.addWidget(self.reject_polygon_button)

        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.view)

        self.drawing_mode = 0
        self.frame_type = 2
        self.polygon_points = []
        self.polygon_lines = []
        self.polygon_colors = [Qt.GlobalColor.blue, Qt.GlobalColor.green]
        self.polygons = [[], []]
        self.last_line = None

        self.setLayout(self.layout)

        self.load_image(frame_path)

    def load_image(self, frame_path):
        pixmap = QPixmap(frame_path).scaled(
            1280,
            720,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if pixmap.isNull():
            print(f"Failed to load image: {frame_path}")
            return
        self.scene.addItem(QGraphicsPixmapItem(pixmap))
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def activate_pan_mode(self, toggle):
        self.view.set_cursor_mode(toggle)

    def confirm_polygon(self):

        for point in self.polygon_points:
            self.scene.removeItem(point)
        for line in self.polygon_lines:
            self.scene.removeItem(line)

        polygon_group = QGraphicsItemGroup()
        for point in self.polygon_points:
            polygon_group.addToGroup(point)
        for line in self.polygon_lines:
            polygon_group.addToGroup(line)
        polygon_group.setFlags(
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable
        )
        self.scene.addItem(polygon_group)
        self.polygons[self.frame_type].append(polygon_group)
        self.reset_polygon()

    def reject_polygon(self):
        for point in self.polygon_points:
            self.scene.removeItem(point)
        for line in self.polygon_lines:
            self.scene.removeItem(line)
        self.reset_polygon()

    def reset_polygon(self):
        self.in_frame_button.setDisabled(False)
        self.out_frame_button.setDisabled(False)
        self.pan_mode_button.setDisabled(False)
        self.confirm_polygon_button.setVisible(False)
        self.reject_polygon_button.setVisible(False)
        self.drawing_mode = 0
        self.frame_type = 2

        self.polygon_points.clear()
        self.polygon_lines.clear()
        if self.last_line:
            self.scene.removeItem(self.last_line)
            self.last_line = None

    def activate_in_frame_drawing(self):
        self.frame_type = 0
        self.activate_polygon_drawing()

    def activate_out_frame_drawing(self):
        self.frame_type = 1
        self.activate_polygon_drawing()

    def activate_polygon_drawing(self):
        self.drawing_mode = 1
        if self.pan_mode_button.isChecked():
            self.pan_mode_button.toggle()

        self.in_frame_button.setDisabled(True)
        self.out_frame_button.setDisabled(True)
        self.pan_mode_button.setDisabled(True)
        self.reject_polygon_button.setVisible(True)

    def eventFilter(self, source, event: QEvent):
        if self.view.cursore_mode == 0 and self.drawing_mode:
            if event.type() == event.Type.MouseButtonPress:
                scene_pos = self.view.mapToScene(event.pos())
                self.add_polygon_point(scene_pos)
            elif event.type() == event.Type.MouseMove and len(self.polygon_points) > 0:
                if self.last_line:
                    self.scene.removeItem(self.last_line)
                scene_pos = self.view.mapToScene(event.pos())
                self.last_line = self.scene.addLine(
                    self.polygon_points[-1].rect().center().x(),
                    self.polygon_points[-1].rect().center().y(),
                    scene_pos.x(),
                    scene_pos.y(),
                    pen=QPen(self.polygon_colors[self.frame_type], 2),
                )
                self.last_line.setZValue(0)

        return super().eventFilter(source, event)

    def add_polygon_point(self, point):
        if self.polygon_points and self.polygon_points[0].contains(point):
            self.deactivate_polygon_drawing()
            return
        if len(self.polygon_points) > 0:
            line = self.scene.addLine(
                self.polygon_points[-1].rect().center().x(),
                self.polygon_points[-1].rect().center().y(),
                point.x(),
                point.y(),
                pen=QPen(self.polygon_colors[self.frame_type], 2),
            )
            line.setZValue(0)
            self.polygon_lines.append(line)
        dot = self.scene.addEllipse(
            point.x() - 5,
            point.y() - 5,
            10,
            10,
            pen=QPen(Qt.GlobalColor.black),
            brush=QBrush(Qt.GlobalColor.red),
        )
        dot.setZValue(1)
        self.polygon_points.append(dot)

    def deactivate_polygon_drawing(self):
        line = self.scene.addLine(
            self.polygon_points[-1].rect().center().x(),
            self.polygon_points[-1].rect().center().y(),
            self.polygon_points[0].rect().center().x(),
            self.polygon_points[0].rect().center().y(),
            pen=QPen(self.polygon_colors[self.frame_type], 2),
        )
        line.setZValue(0)
        self.polygon_lines.append(line)
        if self.last_line:
            self.scene.removeItem(self.last_line)
            self.last_line = None
        self.confirm_polygon_button.setVisible(True)
        self.drawing_mode = 0

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            deleted_items = [[], []]
            for frame_type in range(2):
                for polygon in self.polygons[frame_type]:
                    if polygon.isSelected():
                        self.scene.removeItem(polygon)
                        deleted_items[frame_type].append(polygon)
            for frame_type in range(2):
                for item in deleted_items[frame_type]:
                    self.polygons[frame_type].remove(item)
        return super().keyPressEvent(event)


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
        self.min_zoom = 0.5
        self.max_zoom = 7.0
        self.current_zoom = 1.0
        # 0 - for regular mode
        # 1 - for panning mode
        self.cursore_mode = 0
        self.last_pan_point = None

    def set_cursor_mode(self, mode):
        self.cursore_mode = mode
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
        if self.cursore_mode == 1 and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_pan_point = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.cursore_mode == 1 and self.last_pan_point is not None:
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
        if self.cursore_mode == 1 and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.last_pan_point = None
        else:
            super().mouseReleaseEvent(event)


# TODO special polygon creating mode {add visual frames, probably like warning zone}
# TODO delete selected polygons [on delete button]
