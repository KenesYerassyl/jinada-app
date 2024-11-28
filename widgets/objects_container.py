from PyQt6.QtWidgets import QListView, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex
from widgets.object_uploader import ObjectUploaderDialog
from widgets.object_modifier import ObjectModifierDialog
from local_db.object import Object, ObjectRecord
from local_db.db import (
    get_all_object_ids_and_names,
    insert_object_and_record,
)
from widgets.communicators import ObjectContainerCommunicator


class ObjectContainerModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.objects = get_all_object_ids_and_names()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.objects)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        obj = self.objects[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return obj[1]
        if role == Qt.ItemDataRole.UserRole:
            return obj[0]
        return None

    def get_object(self, index):
        if 0 <= index <= self.rowCount():
            return self.objects[index]
        return None

    def add_object(self, object, object_record):
        insert_object_and_record(object, object_record)
        self.refresh()

    def refresh(self):
        self.beginResetModel()
        self.objects = get_all_object_ids_and_names()
        self.endResetModel()


class ObjectsContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.model = ObjectContainerModel()
        self.communicator = ObjectContainerCommunicator()

        self.add_button = QPushButton()
        self.add_button.setText("Add object")
        self.add_button.clicked.connect(self.invoke_object_uploader_dialog)

        self.list = QListView()
        self.list.setModel(self.model)
        self.list.clicked.connect(self.on_item_clicked)

        self.object_layout = QVBoxLayout()
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.object_layout.addWidget(self.add_button)
        self.object_layout.addWidget(self.list)

        self.setLayout(self.object_layout)

    def invoke_object_uploader_dialog(
        self, object: Object, object_record: ObjectRecord = None
    ):
        object_uploader_dialog = ObjectUploaderDialog(object, self, object_record)
        object_uploader_dialog.communicator.object_uploaded.connect(
            self.invoke_object_modifier_dialog
        )
        object_uploader_dialog.open()

    def invoke_object_modifier_dialog(
        self, object: Object, object_record: ObjectRecord = None
    ):
        object_modifier_dialog = ObjectModifierDialog(object, self, object_record)
        object_modifier_dialog.communicator.object_modification_cancelled.connect(
            self.invoke_object_uploader_dialog
        )
        object_modifier_dialog.communicator.object_modified.connect(self.add_new_object)
        object_modifier_dialog.open()

    def add_new_object(self, object: Object, object_record: ObjectRecord):
        # TODO Process the recording

        self.model.add_object(object, object_record)

    def on_item_clicked(self, index):
        object_index = self.model.data(index, Qt.ItemDataRole.UserRole)
        self.communicator.item_clicked.emit(object_index)
