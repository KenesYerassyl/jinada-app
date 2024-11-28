from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget


class FileUploadWidget(QWidget):
    uploaded = pyqtSignal(str)
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("file_upload")

        self.setStyleSheet(
            """
            #file_upload {
                background-color: #ffffff;
                margin: 5px;
                padding: 20px;
            }
            
            #file_upload_area {
                background-color: #ffffff;
                border: 2px dashed #6c63ff;
                border-radius: 5px;
                margin: 5px;
                padding: 20px;
            }

            QLabel {
                font-size: 14px;
                color: #6c63ff;
            }
            """
        )
        self.setAcceptDrops(True)
        self.clicked.connect(self.browse_files)
        main_layout = QVBoxLayout()

        self.drag_drop_area = QWidget()
        self.drag_drop_area.setObjectName("file_upload_area")
        self.drag_drop_layout = QVBoxLayout(self.drag_drop_area)
        self.drag_drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QSvgWidget("./resources/icons/file-plus.svg")
        self.icon_label.setFixedSize(40, 40)
        self.drag_drop_layout.addWidget(self.icon_label)
        self.drag_drop_layout.setAlignment(
            self.icon_label, Qt.AlignmentFlag.AlignCenter
        )

        self.label = QLabel("Drag and drop a file here or click 'Browse' to select.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_layout.addWidget(self.label)

        main_layout.addWidget(self.drag_drop_area)
        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.uploaded.emit(file_path)
            event.accept()
        else:
            event.ignore()

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File")
        for file_path in file_paths:
            self.uploaded.emit(file_path)
