from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListView,
    QHBoxLayout,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QPolygonF
from PyQt6.QtCore import Qt, QAbstractListModel, QPointF
from local_db.db import (
    insert_record,
    get_all_object_records_datetimes,
    get_object_by_id,
    update_object_by_id,
)
from utils.pyqtgui_utils import rescale_pixmap
from widgets.file_upload import FileUploadWidget
from widgets.object_modifier import ObjectModifierDialog
from widgets.date_picker import DatePickerDialog


class ObjectView(QScrollArea):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)
        self.model = ObjectViewModel(self)

        self.object_layout = QVBoxLayout()
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.object_name = QLabel("Object Frame")

        self.object_frame = QLabel("Select an object.")
        self.object_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tools_layout = QHBoxLayout()
        self.modify_frames_button = QPushButton("Modify Frames")
        self.modify_frames_button.setDisabled(True)
        self.modify_frames_button.clicked.connect(self.modify_frames_button_clicked)
        self.export_data_button = QPushButton("Export Data")
        self.export_data_button.clicked.connect(self.export_data_button_clicked)
        self.export_data_button.setDisabled(True)
        self.tools_layout.addWidget(self.modify_frames_button)
        self.tools_layout.addWidget(self.export_data_button)

        self.file_upload = FileUploadWidget()
        self.file_upload.setHidden(True)
        # TODO self.file_upload.uploaded.connect()

        self.records_list = QListView()
        self.records_list.setModel(self.model)
        # TODO self.records_list.clicked.connect(self.on_item_clicked)

        self.object_layout.addWidget(self.object_name)
        self.object_layout.addWidget(self.object_frame)
        self.object_layout.addLayout(self.tools_layout)
        self.object_layout.addWidget(self.file_upload)
        self.object_layout.addWidget(self.records_list)
        self.setLayout(self.object_layout)

    def load_object(self, object_id):
        self.model.object_id = object_id
        self.model.refresh()
        self.load_view()

    def load_view(self):
        object = get_object_by_id(self.model.object_id)
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

    def modify_frames_button_clicked(self):
        object = get_object_by_id(self.model.object_id)
        object_modifier_dialog = ObjectModifierDialog(
            "",
            object["frame_path"],
            object["name"],
            object["in_frame"],
            object["out_frame"],
            parent=self,
        )
        object_modifier_dialog.communicator.object_modified.connect(
            self.model.modify_object
        )
        object_modifier_dialog.open()

    def export_data_button_clicked(self):
        data_exporter_dialog = DatePickerDialog(self)
        # TODO connect to data_exporter_dialog.date_picked
        data_exporter_dialog.open()


class ObjectViewModel(QAbstractListModel):

    def __init__(self, object_view: ObjectView):
        super().__init__(object_view)
        self.object_view = object_view
        self.object_records = []
        self.object_id = -1

    def rowCount(self, parent=Qt.ItemDataRole.DisplayRole):
        return len(self.object_records)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        obj = self.object_records[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return obj
        if role == Qt.ItemDataRole.UserRole:
            # TODO
            return "some data"
        return None

    def get_object(self, index):
        if 0 <= index <= self.rowCount():
            return self.object_records[index]
        return None

    def add_object_record(self, object_record):
        insert_record(self.object_id, object_record)
        self.refresh()

    def modify_object(self, name, file_path, frame_path, in_frame, out_frame):
        update_object_by_id(self.object_id, name, in_frame, out_frame)
        self.object_view.load_view()

    def refresh(self):
        self.beginResetModel()
        self.object_records = get_all_object_records_datetimes(self.object_id)
        self.endResetModel()
