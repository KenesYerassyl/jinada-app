from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QThread
from db.db import get_object_by_id, update_object_by_id
from utils.pyqtgui_utils import rescale_pixmap
from utils.constants import AppLabels
from widgets.file_upload import FileUploadWidget
from widgets.object_modifier import ObjectModifierDialog
from widgets.date_picker import DatePickerDialog
from widgets.record_list import RecordListWidget
from widgets.shadowed_widget import ShadowedWidget
from utils.data_exporting_worker import DataExportingWorker
import datetime
import logging
import traceback

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
        self.object_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        try:
            self.records_list.object_id = object_id
            self.records_list.load_data()

            object = get_object_by_id(self.records_list.object_id)
            if not object:
                raise ValueError("Object not found.")
            # name
            self.object_name.setText(object["name"])
            # object frame
            self.pixmap = rescale_pixmap(QPixmap(object["frame_path"]))
            painter = QPainter(self.pixmap)

            painter.setPen(QPen(Qt.GlobalColor.blue, 2))
            for polygon in object["in_frames"]:
                frame_polygon = QPolygonF()
                for points in polygon:
                    frame_polygon.append(QPointF(points[0], points[1]))
                painter.drawPolygon(frame_polygon)

            painter.end()
            self.object_frame.setPixmap(rescale_pixmap(self.pixmap, int(self.width() * 0.9)))

            self.modify_frames_button.setDisabled(False)
            self.date_picker_button.setDisabled(False)
            self.file_upload.setHidden(False)
        except Exception as e:
            logging.error(f"Error loading object with ID {object_id}: {e}")
            self.reset()
    
    def modify_frames_button_clicked(self):
        try:
            object = get_object_by_id(self.records_list.object_id)
            object_modifier_dialog = ObjectModifierDialog(
                "",
                object["frame_path"],
                object["name"],
                object["in_frames"],
                parent=self,
            )
            object_modifier_dialog.object_modified.connect(self.modify_object)
            object_modifier_dialog.open()
        except Exception as e:
            logging.error(f"{traceback.format_exc()} Error modifying object with ID {self.records_list.object_id}: {e}")

    def modify_object(self, name, file_path, frame_path, in_frames):
        update_object_by_id(self.records_list.object_id, name, in_frames)
        self.load_object(self.records_list.object_id)

    def date_picker_button_clicked(self):
        date_picker_dialog = DatePickerDialog(self)
        date_picker_dialog.date_picked.connect(self.get_filepath)
        date_picker_dialog.open()

    def get_filepath(self, start_date: datetime.date, end_date: datetime.date):
        self.thread = QThread()

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)")

        if file_path:
            self.worker = DataExportingWorker(start_date, end_date, self.records_list.object_id, file_path)
            self.worker.moveToThread(self.thread)

            self.worker.finished.connect(self.on_export_finished)
            self.worker.error.connect(self.on_export_error)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.date_picker_button.setEnabled(False)

    def on_export_finished(self):
        self.date_picker_button.setEnabled(True)

    def on_export_error(self, error_msg):
        QMessageBox.critical(self, error_msg, None, buttons=QMessageBox.StandardButton.Ok)
        self.date_picker_button.setEnabled(True)

    def resizeEvent(self, event):
        if self.pixmap is not None:
            new_width = int(self.width() * 0.9)
            if self.object_frame.pixmap() is None or self.object_frame.pixmap().width() != new_width:
                self.object_frame.setPixmap(rescale_pixmap(self.pixmap, new_width))
        return super().resizeEvent(event)
