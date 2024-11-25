from PyQt6.QtWidgets import QListWidget, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from widgets.object_uploader import ObjectUploaderDialog
from widgets.object_modifier import ObjectModifierDialog
from utils.object import default_object


class ObjectsContainer(QWidget):
    def __init__(self):
        super().__init__()

        self.add_button = QPushButton()
        self.add_button.setText("Add object")
        self.add_button.clicked.connect(self.invoke_object_uploader_dialog)

        self.list = QListWidget()

        self.object_layout = QVBoxLayout()
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.object_layout.addWidget(self.add_button)
        self.object_layout.addWidget(self.list)

        self.setLayout(self.object_layout)

    def invoke_object_uploader_dialog(self):
        object_uploader_dialog = ObjectUploaderDialog(self)
        object_uploader_dialog.accepted.connect(self.invoke_object_modifier_dialog)
        object_uploader_dialog.open()

    def invoke_object_modifier_dialog(self):
        object_modifier_dialog = ObjectModifierDialog(default_object, self)
        object_modifier_dialog.rejected.connect(self.invoke_object_uploader_dialog)
        object_modifier_dialog.accepted.connect(self.add_new_object)
        object_modifier_dialog.open()

    def add_new_object(self):
        # TODO add new obj to DB
        pass
