from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.file_upload import FileUploadWidget
from local_db.db_fs import save_first_frame, delete_file
from utils.constants import AppLabels, Error


class ObjectUploaderDialog(QDialog):
    object_uploaded = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(AppLabels().OBJECT_UPLOADER_DIALOG_TITLE)
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.file_path = ""
        self.frame_path = ""

        layout = QVBoxLayout()

        # file upload widget
        self.file_upload = FileUploadWidget()
        self.file_upload.uploaded.connect(self.video_uploaded)
        # current status label
        self.status_label = QLabel(AppLabels().STATUS_LABEL)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # buttons
        self.next_button = QPushButton(AppLabels().NEXT_BUTTON)
        self.next_button.setDisabled(True)
        self.next_button.setObjectName("dialog-button-positive")
        self.next_button.clicked.connect(self.on_next)
        self.cancel_button = QPushButton(AppLabels().CANCEL_BUTTON)
        self.cancel_button.setObjectName("dialog-button-negative")
        self.cancel_button.clicked.connect(self.on_cancel)

        self.button_box = QDialogButtonBox(self)
        self.button_box.addButton(
            self.next_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )

        layout.addWidget(self.file_upload)
        layout.addWidget(self.status_label)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def video_uploaded(self, file_path):
        upload_result = save_first_frame(file_path)

        if upload_result[0] == 0:
            QMessageBox.critical(
                self,
                Error().ERROR_DURING_UPLOAD,
                upload_result[1],
                buttons=QMessageBox.StandardButton.Ok,
            )
        else:
            self.file_path = file_path
            self.frame_path = upload_result[1]
            self.status_label.setText(f"{AppLabels().STATUS_LABEL_UPDATED} {file_path}")

        self.next_button.setDisabled(self.file_path == "" or self.frame_path == "")

    def on_next(self):
        self.object_uploaded.emit(self.file_path, self.frame_path)
        self.accept()

    def on_cancel(self):
        delete_file(self.frame_path)
        self.reject()
