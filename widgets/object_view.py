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
from widgets.data_presenter import DataPresenterWidget
from widgets.record_list import RecordListWidget
from utils.constants import AppLabels
from widgets.shadowed_widget import ShadowedWidget


class ObjectView(ShadowedWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)
        self.setObjectName("ObjectView")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        object_layout = QVBoxLayout()
        object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.object_name = QLabel(AppLabels().OBJECT_NAME)
        self.object_name.setObjectName("ObjectView-object_name")

        self.object_frame = QLabel(AppLabels().OBJECT_FRAME)
        self.object_frame.setObjectName("ObjectView-object_frame")
        self.object_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixmap = None

        self.modify_frames_button = QPushButton(AppLabels().MODIFY_FRAMES_BUTTON)
        self.modify_frames_button.clicked.connect(self.modify_frames_button_clicked)
        self.modify_frames_button.setObjectName("active_button")
        self.date_picker_button = QPushButton(AppLabels().DATE_PICKER_BUTTON)
        self.date_picker_button.clicked.connect(self.date_picker_button_clicked)
        self.date_picker_button.setObjectName("active_button")
        tools_layout = QHBoxLayout()
        tools_layout.addWidget(self.modify_frames_button)
        tools_layout.addWidget(self.date_picker_button)
        tools_layout.setContentsMargins(50, 0, 50, 0)
        tools_layout.setSpacing(10)

        self.records_list = RecordListWidget(-1)

        self.file_upload = FileUploadWidget()
        self.file_upload.uploaded.connect(self.records_list.add_record)

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
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setObjectName("ObjectView-scroll_area")
        layout = QVBoxLayout()
        layout.addWidget(self.object_name)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)
        self.reset()

    def reset(self):
        self.object_name.setText(AppLabels().OBJECT_NAME)
        self.object_frame.setText(AppLabels().OBJECT_FRAME)
        self.modify_frames_button.setDisabled(True)
        self.date_picker_button.setDisabled(True)
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
        self.pixmap = rescale_pixmap(QPixmap(object["frame_path"]))
        painter = QPainter(self.pixmap)

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
        self.object_frame.setPixmap(rescale_pixmap(self.pixmap, int(self.width() * 0.9)))

        self.modify_frames_button.setDisabled(False)
        self.date_picker_button.setDisabled(False)
        self.file_upload.setHidden(False)
    
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

    def date_picker_button_clicked(self):
        data_picker_dialog = DatePickerDialog(self)
        data_picker_dialog.date_picked.connect(self.show_data)
        data_picker_dialog.open()

    def show_data(self, start_date, end_date):
        self.date_presenter = DataPresenterWidget(
            self.records_list.object_id, start_date, end_date
        )
        self.date_presenter.show()

    def resizeEvent(self, event):
        if self.pixmap is not None:
            self.object_frame.setPixmap(rescale_pixmap(self.pixmap, int(self.width() * 0.9)))
        return super().resizeEvent(event)
