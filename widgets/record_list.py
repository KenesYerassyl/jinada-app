from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
    QProgressBar,
)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from local_db.object import ObjectRecord
from local_db.db import (
    get_all_records_for_list,
    insert_record,
    delete_record_by_id,
    update_record_status,
)
from datetime import datetime
from utils.cvpm import CentralVideoProcessingManager


class RecordListItem(QWidget):

    delete_clicked = pyqtSignal(int)

    def __init__(self, record_id, file_path, date: datetime, is_processed: bool):
        super().__init__()
        self.record_id = record_id

        vertical_layout1 = QVBoxLayout()
        self.record_date = QLabel(date.strftime("%Y-%m-%d %H:%M:%S"))
        self.file_path = QLabel(file_path)
        vertical_layout1.addWidget(self.record_date)
        vertical_layout1.addWidget(self.file_path)

        horizontal_layout1 = QHBoxLayout()
        self.done_icon = QSvgWidget("./resources/icons/confirm.svg")
        self.done_icon.setHidden(not is_processed)
        self.done_icon.setFixedSize(20, 20)

        self.delete_button = QPushButton(icon=QIcon("./resources/icons/trash.svg"))
        self.delete_button.setIconSize(QSize(20, 20))
        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background: transparent;
                padding: 0;
            }
            QPushButton:hover {
                background: transparent;
            }
        """
        )

        horizontal_layout1.addLayout(vertical_layout1)
        horizontal_layout1.addStretch(1)
        horizontal_layout1.addWidget(self.done_icon)
        horizontal_layout1.addWidget(self.delete_button)

        vertical_layout2 = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setHidden(is_processed)

        vertical_layout2.addLayout(horizontal_layout1)
        vertical_layout2.addWidget(self.progress_bar)
        vertical_layout2.setSpacing(5)
        self.setLayout(vertical_layout2)

    def delete_button_clicked(self):
        self.delete_clicked.emit(self.record_id)

    def setProgress(self, new_value):
        self.progress_bar.setValue(new_value)


class RecordListWidget(QListWidget):

    record_deleted = pyqtSignal()

    def __init__(self, object_id):
        super().__init__()
        self.object_id = object_id
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        CentralVideoProcessingManager().progress_updated.connect(self.record_updated)
        CentralVideoProcessingManager().finished.connect(
            self.record_finished_processing
        )
        self.load_data()

    def load_data(self):
        self.clear()
        in_progress = {}
        if self.object_id in CentralVideoProcessingManager().tasks:
            for task in CentralVideoProcessingManager().tasks[self.object_id]:
                in_progress[task["record_id"]] = task["progress"]
        records = get_all_records_for_list(self.object_id)
        for record in records:
            new_list_item = RecordListItem(record[0], record[1], record[2], record[3])
            if not record[3]:
                if record[0] in in_progress:
                    new_list_item.setProgress(in_progress[record[0]])
                else:
                    CentralVideoProcessingManager().add_task(self.object_id, record[0])
            new_list_item.delete_clicked.connect(self.remove_record)
            old_list_item = QListWidgetItem()
            old_list_item.setSizeHint(QSize(200, 80))
            self.addItem(old_list_item)
            self.setItemWidget(old_list_item, new_list_item)
        if len(records) > 0:
            self.setFixedHeight(self.count() * self.sizeHintForRow(0))
        else:
            self.setMinimumHeight(self.minimumSizeHint().width())
            self.setMaximumHeight(16777215)

    def add_record(self, file_path):
        object_record = ObjectRecord(file_path)
        try:
            record_id = insert_record(self.object_id, object_record)
            CentralVideoProcessingManager().add_task(self.object_id, record_id)
            self.load_data()
        except Exception as e:
            print(f"Unexpected error occured while adding a record: {e}")

    def remove_record(self, record_id):
        try:
            # TODO terminate task if it is actively processing record
            delete_record_by_id(record_id)
            for i in range(self.count()):
                widget: RecordListItem = self.itemWidget(self.item(i))
                if widget.record_id == record_id:
                    self.takeItem(i)
                    break
        except Exception as e:
            print(f"Unexpected error occured while deleting a record: {e}")

    def record_updated(self, object_id, record_id, progress):
        if object_id == self.object_id:
            for i in range(self.count()):
                widget: RecordListItem = self.itemWidget(self.item(i))
                if widget.record_id == record_id:
                    widget.setProgress(progress)
                    break

    def record_finished_processing(self, object_id, record_id):
        if object_id == self.object_id:
            for i in range(self.count()):
                widget: RecordListItem = self.itemWidget(self.item(i))
                if widget.record_id == record_id:
                    widget.done_icon.setHidden(False)
                    widget.progress_bar.setHidden(True)
