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
from widgets.file_upload import FileUploadWidget
from local_db.object import Object, ObjectRecord
from widgets.communicators import ObjectCommunicator


class ObjectUploaderDialog(QDialog):
    def __init__(
        self, object: Object = None, parent=None, object_record: ObjectRecord = None
    ):
        super().__init__(parent)
        self.setWindowTitle("New object upload")
        # self.setMaximumWidth(self.width())
        # self.setMaximumHeight(self.height())
        self.communicator = ObjectCommunicator()
        layout = QVBoxLayout()
        self.object = object if object else Object()
        self.object_record = object_record if object_record else ObjectRecord()
        # input text
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name...")
        self.name_input.textEdited.connect(self.name_updated)
        self.name_input.setText(object.name if object else "")
        # file upload widget
        self.file_upload = FileUploadWidget()
        self.file_upload.uploaded.connect(self.video_uploaded)
        # current status label
        self.status_label = QLabel(
            object_record.file_path if object_record else "Nothing uploaded"
        )
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
        self.setLayout(layout)

    def name_updated(self):
        self.object.name = self.name_input.text()
        if self.object_record.file_path != "" and self.object.name != "":
            self.next_button.setDisabled(False)
        else:
            self.next_button.setDisabled(True)

    def video_uploaded(self, file_path):
        self.object_record.file_path = file_path
        upload_result = self.object.save_first_frame(file_path)

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

        if self.object_record.file_path != "" and self.object.name != "":
            self.next_button.setDisabled(False)
        else:
            self.next_button.setDisabled(True)

    def on_next(self):
        self.communicator.object_uploaded.emit(self.object, self.object_record)
        self.accept()

    def on_cancel(self):
        self.reject()
