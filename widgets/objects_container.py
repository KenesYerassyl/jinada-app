from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.object_uploader import ObjectUploaderDialog
from widgets.object_modifier import ObjectModifierDialog
from widgets.object_list import ObjectListWidget, ObjectListItem, QListWidgetItem
from utils.constants import AppLabels


class ObjectsContainer(QWidget):
    item_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("ObjectsContainer")

        self.add_button = QPushButton()
        self.add_button.setText(AppLabels().ADD_BUTTON)
        self.add_button.clicked.connect(self.invoke_object_uploader_dialog)
        self.add_button.setObjectName("active_button")

        self.list = ObjectListWidget()
        self.list.itemClicked.connect(self.load_object)
        self.list.setSpacing(10)

        object_layout = QVBoxLayout()
        object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        object_layout.addWidget(self.add_button)
        object_layout.addWidget(self.list)

        self.setLayout(object_layout)

    def invoke_object_uploader_dialog(self):
        object_uploader_dialog = ObjectUploaderDialog(parent=self)
        object_uploader_dialog.object_uploaded.connect(
            self.invoke_object_modifier_dialog
        )
        object_uploader_dialog.open()

    def invoke_object_modifier_dialog(self, file_path, frame_path):
        object_modifier_dialog = ObjectModifierDialog(
            file_path, frame_path, parent=self
        )
        object_modifier_dialog.object_modification_cancelled.connect(
            self.invoke_object_uploader_dialog
        )
        object_modifier_dialog.object_modified.connect(self.list.add_object)
        object_modifier_dialog.open()

    def load_object(self, item: QListWidgetItem):
        widget: ObjectListItem = self.list.itemWidget(item)
        self.item_clicked.emit(widget.object_id)
