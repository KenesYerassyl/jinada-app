from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from utils.file_upload import FileUploadWidget
from utils.object import Object


class ObjectUploaderDialog(QDialog):
    def __init__(self, parent=None, object: Object = None):
        super().__init__(parent)
        self.setWindowTitle("New object upload")
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        layout = QVBoxLayout(self)

        # input text
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name...")
        self.name_input.textEdited.connect(self.name_updated)
        # file upload widget
        self.file_upload = FileUploadWidget()
        self.file_upload.videoAdded.connect(self.video_uploaded)
        # current status label
        self.status_label = QLabel("Nothing uploaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # buttons
        self.next_button = QPushButton("Next")
        self.next_button.setDisabled(True)
        self.cancel_button = QPushButton("Cancel")
        self.next_button.clicked.connect(self.on_next)
        self.cancel_button.clicked.connect(self.on_cancel)

        self.button_box = QDialogButtonBox(self)
        self.button_box.addButton(
            self.next_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )

        layout.addWidget(self.name_input)
        layout.addWidget(self.file_upload)
        layout.addWidget(self.status_label)
        layout.addWidget(self.button_box)

        if object:
            self.status_label.setText(f"Uploaded file: {object.get_file_path()}")
            self.name_input.setText(object.get_name())

        self.object = object if object else Object()

    def name_updated(self):
        self.object.set_name(self.name_input.text())
        if self.object.get_file_path() != "" and self.object.get_name() != "":
            self.next_button.setDisabled(False)
        else:
            self.next_button.setDisabled(True)

    def video_uploaded(self, file_path):
        self.object.set_file_path(file_path)
        upload_result = self.object.save_first_frame()

        if upload_result[0] == 0:
            QMessageBox.critical(
                self,
                "Error during upload",
                upload_result[1],
                buttons=QMessageBox.StandardButton.Ok,
            )
            self.object.set_file_path("")
            self.object.set_frame_path("")
        else:
            self.status_label.setText(f"Uploaded file: {file_path}")
        if self.object.get_file_path() != "" and self.object.get_name() != "":
            self.next_button.setDisabled(False)
        else:
            self.next_button.setDisabled(True)

    def on_next(self):
        self.accept()

    def on_cancel(self):
        self.reject()
