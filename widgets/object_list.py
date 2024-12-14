from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
)
from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon

from local_db.object import Object, ObjectRecord
from local_db.db import (
    get_all_objects_for_list,
    insert_object,
    delete_object_by_id,
    insert_record,
)
from datetime import datetime
from utils.cvpm import CentralVideoProcessingManager
from utils.constants import Error
from paths import Paths


class ObjectListItem(QWidget):

    delete_clicked = pyqtSignal(int)

    def __init__(self, object_id, name, date: datetime):
        super().__init__()
        info_layout = QVBoxLayout()

        self.object_name = QLabel(name)
        self.object_name.setObjectName("ObjectListItem-object_name")
        self.object_id = object_id
        self.object_date = QLabel(date.strftime("%Y-%m-%d %H:%M:%S"))
        self.object_date.setObjectName("ObjectListItem-object_date")

        info_layout.addWidget(self.object_name)
        info_layout.addWidget(self.object_date)

        self.delete_button = QPushButton(icon=QIcon(Paths.TRASH_ICON))
        self.delete_button.setObjectName("ObjectListItem-delete_button")
        self.delete_button.setIconSize(QSize(20, 20))
        self.delete_button.clicked.connect(self.delete_button_clicked)

        layout = QHBoxLayout()
        layout.addLayout(info_layout)
        layout.addStretch(1)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def delete_button_clicked(self):
        self.delete_clicked.emit(self.object_id)


class ObjectListWidget(QListWidget):

    object_deleted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("ObjectListWidget")
        self.load_data()

    def load_data(self):
        self.clear()
        objects = get_all_objects_for_list()
        for object in objects:
            new_list_item = ObjectListItem(object[0], object[1], object[2])
            new_list_item.delete_clicked.connect(self.remove_object)
            old_list_item = QListWidgetItem()
            old_list_item.setSizeHint(QSize(200, 60))
            self.addItem(old_list_item)
            self.setItemWidget(old_list_item, new_list_item)

    def add_object(self, name, file_path, frame_path, in_frame, out_frame):
        object = Object(name, frame_path, in_frame, out_frame)
        object_record = ObjectRecord(file_path)
        try:
            object_id = insert_object(object)
            record_id = insert_record(object_id, object_record)
            CentralVideoProcessingManager().add_task(object_id, record_id)
            self.load_data()
        except Exception as e:
            print(f"{Error().ERROR_WHILE_ADDING_OBJECT} {e}")

    def remove_object(self, object_id):
        try:
            # TODO: Cancel all running tasks, and notify the user about it
            delete_object_by_id(object_id)
            for i in range(self.count()):
                widget: ObjectListItem = self.itemWidget(self.item(i))
                if widget.object_id == object_id:
                    self.takeItem(i)
                    break
            self.object_deleted.emit()
        except Exception as e:
            print(f"{Error().ERROR_WHILE_DELETING_OBJECT} {e}")
