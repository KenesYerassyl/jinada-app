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

from db.object import Object, ObjectRecord
from db.db import (
    get_all_objects_for_list,
    insert_object,
    delete_object_by_id,
    insert_record,
)
from datetime import datetime
from utils.cvpm import CentralVideoProcessingManager
from paths import Paths
from typing import List, Tuple
import logging

class ObjectListItem(QWidget):

    delete_clicked = pyqtSignal(int)

    def __init__(self, object_id: int, name: str, date: datetime):
        super().__init__()
        self.object_id = object_id
        self.object_name_text = name
        self.object_date_time = date
        self.setup_ui()

    def setup_ui(self):
        info_layout = QVBoxLayout()

        self.object_name = QLabel(self.object_name_text)
        self.object_name.setObjectName("ObjectListItem-object_name")
        
        self.object_date = QLabel(self.object_date_time.strftime("%Y-%m-%d %H:%M:%S"))
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
        try:
            self.clear()
            objects = get_all_objects_for_list()
            for object in objects:
                new_list_item = ObjectListItem(object[0], object[1], object[2])
                new_list_item.delete_clicked.connect(self.remove_object)
                old_list_item = QListWidgetItem()
                old_list_item.setSizeHint(QSize(200, 65))
                self.addItem(old_list_item)
                self.setItemWidget(old_list_item, new_list_item)
        except Exception as e:
            logging.error(f"Error while loading data to Object List: {e}")
            

    def add_object(self, name: str, file_path: str, frame_path: str, in_frame: List[List[Tuple[int, int]]], out_frame: List[List[Tuple[int, int]]]):
        object = Object(name, frame_path, in_frame, out_frame)
        object_record = ObjectRecord(file_path)
        try:
            object_id = insert_object(object)
            record_id = insert_record(object_id, object_record)
            CentralVideoProcessingManager().add_task(object_id, record_id)
            self.load_data()
        except Exception as e:
            logging.error(f"Unexpected error occurred when trying to add an object: {e}")

    def remove_object(self, object_id: int):
        try:
            CentralVideoProcessingManager().cancel_tasks(object_id)
            delete_object_by_id(object_id)
            for i in range(self.count()):
                widget: ObjectListItem = self.itemWidget(self.item(i))
                if widget and widget.object_id == object_id:
                    self.takeItem(i)
                    break
            self.object_deleted.emit()
        except Exception as e:
            logging.error(f"Unexpected error occurred when trying to delete an object: {e}")
