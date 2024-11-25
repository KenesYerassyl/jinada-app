from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QSize


class ObjectView(QScrollArea):

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(800)

        self.object_layout = QVBoxLayout()
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.placeholder_name = QLabel("Illustration Frame")
        self.placeholder_name.setStyleSheet("background-color: black; color: white;")
        self.placeholder_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.object_info = QLabel("Select an object.")
        self.object_info.setWordWrap(True)

        self.object_layout.addWidget(self.placeholder_name)
        self.object_layout.addWidget(self.object_info)

        self.setLayout(self.object_layout)
