from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from local_db.db import (
    get_object_by_id,
    update_object_by_id,
)
from utils.pyqtgui_utils import rescale_pixmap
from widgets.file_upload import FileUploadWidget
from widgets.object_modifier import ObjectModifierDialog
from widgets.date_picker import DatePickerDialog
from widgets.record_list import RecordListWidget


class ObjectView(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)

        object_layout = QVBoxLayout()
        object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.object_name = QLabel("Object Frame")

        self.object_frame = QLabel("Select an object.")
        self.object_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.modify_frames_button = QPushButton("Modify Frames")
        self.modify_frames_button.clicked.connect(self.modify_frames_button_clicked)
        self.export_data_button = QPushButton("Export Data")
        self.export_data_button.clicked.connect(self.export_data_button_clicked)
        tools_layout = QHBoxLayout()
        tools_layout.addWidget(self.modify_frames_button)
        tools_layout.addWidget(self.export_data_button)

        self.records_list = RecordListWidget(-1)

        self.file_upload = FileUploadWidget()
        self.file_upload.uploaded.connect(self.records_list.add_record)

        object_layout.addWidget(self.object_name)
        object_layout.addWidget(self.object_frame)
        object_layout.addLayout(tools_layout)
        object_layout.addWidget(self.file_upload)
        object_layout.addWidget(self.records_list)

        self.container = QWidget()
        self.container.setLayout(object_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)
        self.reset()

    def reset(self):
        self.object_name.setText("Object Frame")
        self.object_frame.setText("Select an object.")
        self.modify_frames_button.setDisabled(True)
        self.export_data_button.setDisabled(True)
        self.file_upload.setHidden(True)
        self.records_list.object_id = -1
        self.records_list.load_data()

    def load_object(self, object_id):
        self.records_list.object_id = object_id
        self.records_list.load_data()

        object = get_object_by_id(self.records_list.object_id)
        # name
        self.object_name.setText(object["name"])
        # object frame
        pixmap = rescale_pixmap(QPixmap(object["frame_path"]))
        painter = QPainter(pixmap)

        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        for polygon in object["in_frame"]:
            frame_polygon = QPolygonF()
            for points in polygon:
                frame_polygon.append(QPointF(points[0], points[1]))
            painter.drawPolygon(frame_polygon)

        painter.setPen(QPen(Qt.GlobalColor.green, 2))
        for polygon in object["out_frame"]:
            frame_polygon = QPolygonF()
            for points in polygon:
                frame_polygon.append(QPointF(points[0], points[1]))
            painter.drawPolygon(frame_polygon)

        painter.end()
        self.object_frame.setPixmap(pixmap)
        self.object_frame.resize(pixmap.width(), pixmap.height())

        self.modify_frames_button.setDisabled(False)
        self.export_data_button.setDisabled(False)
        self.file_upload.setHidden(False)

    # def resizeEvent(self, event):
    #     if self.records_list.object_id != -1:
    #         self.object_frame.setPixmap(
    #             rescale_pixmap(self.object_frame.pixmap(), self.object_frame.width())
    #         )
    #     return super().resizeEvent(event)

    def modify_frames_button_clicked(self):
        object = get_object_by_id(self.records_list.object_id)
        object_modifier_dialog = ObjectModifierDialog(
            "",
            object["frame_path"],
            object["name"],
            object["in_frame"],
            object["out_frame"],
            parent=self,
        )
        object_modifier_dialog.object_modified.connect(self.modify_object)
        object_modifier_dialog.open()

    def modify_object(self, name, file_path, frame_path, in_frame, out_frame):
        update_object_by_id(self.records_list.object_id, name, in_frame, out_frame)
        self.load_object(self.records_list.object_id)

    def export_data_button_clicked(self):
        data_exporter_dialog = DatePickerDialog(self)
        # TODO connect to data_exporter_dialog.date_picked
        data_exporter_dialog.open()
