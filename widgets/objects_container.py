from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from widgets.object_uploader import ObjectUploaderDialog
from widgets.object_modifier import ObjectModifierDialog
from widgets.object_list import ObjectListWidget, ObjectListItem, QListWidgetItem
from widgets.generic_button import GenericButton
from widgets.shadowed_widget import ShadowedWidget
from utils.constants import AppLabels
from paths import Paths
import logging



class ObjectsContainer(ShadowedWidget):
    item_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("ObjectsContainer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = QLabel(AppLabels().OBJECT_LIST)
        self.label.setObjectName("ObjectsContainer-label")

        self.add_button = GenericButton(icon_normal=Paths.PLUS_ICON, icon_pressed=Paths.PLUS_CLICKED_ICON)
        self.add_button.setIconSize(QSize(25, 25))
        self.add_button.clicked.connect(self.invoke_object_uploader_dialog)
        self.add_button.setObjectName("ObjectsContainer-add_button")

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.add_button)
        header_layout.setAlignment(self.add_button, Qt.AlignmentFlag.AlignCenter)

        self.list = ObjectListWidget()
        self.list.itemClicked.connect(self.load_object)
        self.list.setSpacing(10)

        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container_layout.addLayout(header_layout)
        container_layout.addWidget(self.list)

        self.setLayout(container_layout)

    def invoke_object_uploader_dialog(self):
        object_uploader_dialog = ObjectUploaderDialog(parent=self)
        object_uploader_dialog.object_uploaded.connect(self.invoke_object_modifier_dialog)
        object_uploader_dialog.open()

    def invoke_object_modifier_dialog(self, file_path: str, frame_path: str):
        try:
            object_modifier_dialog = ObjectModifierDialog(
                file_path, frame_path, parent=self
            )
            object_modifier_dialog.object_modification_cancelled.connect(
                self.invoke_object_uploader_dialog
            )
            object_modifier_dialog.object_modified.connect(self.list.add_object)
            object_modifier_dialog.open()
        except Exception as e:
            logging.error(f"Something went wrong when working with Object Modifier Dialog: {e}")

    def load_object(self, item: QListWidgetItem):
        widget: ObjectListItem = self.list.itemWidget(item)
        if widget is None:
            logging.error("Error: Item widget not found.")
            return
        self.item_clicked.emit(widget.object_id)
