from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QWidget,
    QGraphicsScene,
    QHBoxLayout,
    QGraphicsPixmapItem,
    QToolButton,
    QGraphicsItemGroup,
    QGraphicsEllipseItem,
)
from PyQt6.QtGui import (
    QPixmap,
    QPen,
    QBrush,
    QIcon,
    QKeyEvent,
)
from PyQt6.QtCore import Qt, QEvent, QRectF, pyqtSignal
from local_db.object import Object
from widgets.communicators import ObjectCommunicator
from widgets.zoompan_graphics_view import ZoomPanGraphicsView
from utils.pyqtgui_utils import rescale_pixmap, copy_ellipse_item, copy_line_item

# TODO 1 We are actually creating new polygons each time, instead we should be able to modify polygons if they existed previously.


class ObjectModifierDialog(QDialog):
    def __init__(self, object: Object, parent=None, object_record=None):
        super().__init__(parent)
        self.object = object
        self.object_record = object_record
        self.communicator = ObjectCommunicator()
        self.setWindowTitle("Object modification")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        layout = QVBoxLayout(self)

        # input text
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name_label.setText(f"Name of the object: {object.name}")
        # initial frame graphics scene
        self.polygon_drawer = PolygonDrawer(object.frame_path)
        # buttons
        self.upload_button = QPushButton("Upload")
        # TODO 2 Later make disability dynamic, refer to TODO 1
        self.upload_button.setDisabled(True)
        self.upload_button.clicked.connect(self.on_upload)
        self.polygon_drawer.polygons_drawn.connect(self.upload_button.setDisabled)

        self.back_button = QPushButton("Back")
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
        for frame_type in range(2):
            for polygon in self.polygon_drawer.polygons[frame_type]:
                polygon_frame = []
                for child_item in polygon.childItems():
                    if isinstance(child_item, QGraphicsEllipseItem):
                        rect = child_item.boundingRect()
                        center = child_item.mapToScene(rect.center())
                        polygon_frame.append((center.x(), center.y()))

                if frame_type == 0:
                    self.object.in_frame.append(polygon_frame)
                else:
                    self.object.out_frame.append(polygon_frame)
        self.communicator.object_modified.emit(self.object, self.object_record)
        self.accept()

    def on_back(self):
        self.communicator.object_modification_cancelled.emit(
            self.object, self.object_record
        )
        self.reject()


class PolygonDrawer(QWidget):

    polygons_drawn = pyqtSignal(bool)

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
        self.reject_polygon_button.clicked.connect(self.activate_normal_mode)

        self.in_frame_button = QPushButton("Add in-frame")
        self.in_frame_button.clicked.connect(self.inframe_button_clicked)

        self.out_frame_button = QPushButton("Add out-frame")
        self.out_frame_button.clicked.connect(self.outframe_button_clicked)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.pan_mode_button)
        self.buttons_layout.addWidget(self.in_frame_button)
        self.buttons_layout.addWidget(self.out_frame_button)
        self.buttons_layout.addWidget(self.confirm_polygon_button)
        self.buttons_layout.addWidget(self.reject_polygon_button)

        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.view)

        self.drawing_mode = 0
        # 0 -> regular mode
        # 1 -> polygon drawing mode
        # 2 -> polygon confirming mode
        self.frame_type = None
        self.polygon_points = []
        self.polygon_lines = []
        self.polygon_colors = [Qt.GlobalColor.blue, Qt.GlobalColor.green]
        self.polygons = [[], []]
        self.last_line = None
        self.setLayout(self.layout)
        self.load_image(frame_path)

    def load_image(self, frame_path):
        pixmap = rescale_pixmap(QPixmap(frame_path))
        if pixmap.isNull():
            print(f"Failed to load image: {frame_path}")
            return
        self.scene.addItem(QGraphicsPixmapItem(pixmap))
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

        self.last_line = self.scene.addLine(0, 0, 0, 0)
        self.last_line.setZValue(0)

    def activate_pan_mode(self, toggle):
        self.view.set_cursor_mode(toggle)

    def inframe_button_clicked(self):
        self.frame_type = 0
        self.activate_polygon_drawing_mode()

    def outframe_button_clicked(self):
        self.frame_type = 1
        self.activate_polygon_drawing_mode()

    def activate_polygon_drawing_mode(self):
        self.drawing_mode = 1
        if self.pan_mode_button.isChecked():
            self.pan_mode_button.toggle()

        self.in_frame_button.setDisabled(True)
        self.out_frame_button.setDisabled(True)
        self.pan_mode_button.setDisabled(True)
        self.reject_polygon_button.setVisible(True)

    def activate_polygon_confirming_mode(self):
        self.drawing_mode = 2
        self.last_line.setLine(0, 0, 0, 0)
        self.confirm_polygon_button.setVisible(True)

    def activate_normal_mode(self):
        self.drawing_mode = 0
        self.last_line.setLine(0, 0, 0, 0)
        self.frame_type = None
        self.in_frame_button.setDisabled(False)
        self.out_frame_button.setDisabled(False)
        self.pan_mode_button.setDisabled(False)
        self.confirm_polygon_button.setVisible(False)
        self.reject_polygon_button.setVisible(False)

        for point in self.polygon_points:
            self.scene.removeItem(point)
        for line in self.polygon_lines:
            self.scene.removeItem(line)
        self.polygon_points.clear()
        self.polygon_lines.clear()

    def add_polygon_point(self, point):
        if self.polygon_points and self.polygon_points[0].contains(point):
            line = self.scene.addLine(
                self.polygon_points[-1].rect().center().x(),
                self.polygon_points[-1].rect().center().y(),
                self.polygon_points[0].rect().center().x(),
                self.polygon_points[0].rect().center().y(),
                pen=QPen(self.polygon_colors[self.frame_type], 2),
            )
            line.setZValue(0)
            self.polygon_lines.append(line)
            self.activate_polygon_confirming_mode()
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

    def confirm_polygon(self):
        polygon_group = QGraphicsItemGroup()
        for point in self.polygon_points:
            polygon_group.addToGroup(copy_ellipse_item(point))
        for line in self.polygon_lines:
            polygon_group.addToGroup(copy_line_item(line))
        polygon_group.setFlags(
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable
        )
        self.scene.addItem(polygon_group)
        self.polygons[self.frame_type].append(polygon_group)
        self.verify_polygons()
        self.activate_normal_mode()

    def eventFilter(self, source, event: QEvent):
        if self.drawing_mode == 1:
            if event.type() == event.Type.MouseButtonPress:
                scene_pos = self.view.mapToScene(event.pos())
                self.add_polygon_point(scene_pos)
            elif event.type() == event.Type.MouseMove and len(self.polygon_points) > 0:
                scene_pos = self.view.mapToScene(event.pos())
                self.last_line.setLine(
                    self.polygon_points[-1].rect().center().x(),
                    self.polygon_points[-1].rect().center().y(),
                    scene_pos.x(),
                    scene_pos.y(),
                )
                self.last_line.setPen(QPen(self.polygon_colors[self.frame_type], 2))

        return super().eventFilter(source, event)

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
        self.verify_polygons()
        return super().keyPressEvent(event)

    def verify_polygons(self):
        self.polygons_drawn.emit(
            not (len(self.polygons[0]) > 0 and len(self.polygons[1]))
        )
