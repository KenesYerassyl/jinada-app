from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal


class FileUploadWidget(QWidget):
    videoAdded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout()

        self.label = QLabel("Drag and drop a file here or click 'Browse' to select.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_files)
        self.layout.addWidget(self.browse_button)

        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.videoAdded.emit(file_path)
            event.accept()
        else:
            event.ignore()

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File")
        for file_path in file_paths:
            self.videoAdded.emit(file_path)
