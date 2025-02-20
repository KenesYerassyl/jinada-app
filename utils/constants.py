from PyQt6.QtCore import QCoreApplication
import os

APP_NAME = "Jinada"
STANDARD_WIDTH = 1280


class Error:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.ERROR_DURING_UPLOAD = QCoreApplication.translate("ObjectUploaderDialog", "Error during uploding")
        self.ERROR_DURING_MODIFICATION = QCoreApplication.translate("ObjectModifierDialog", "Error during modification")
        self.ERROR_DURING_MODIFICATION_DESCRIPTION = QCoreApplication.translate("ObjectModifierDialog", "Polygons are missing or name is empty.")
        self.ERROR_DURING_FILE_EXPORTING = QCoreApplication.translate("DataExportingWorker", "Error during file exporting")

class AppLabels:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.OBJECT_NAME = QCoreApplication.translate("ObjectView", "Object Name")
        self.OBJECT_FRAME = QCoreApplication.translate("ObjectView", "Select an object")
        self.MODIFY_FRAMES_BUTTON = QCoreApplication.translate("ObjectView", "Modify Frames")
        self.DATE_PICKER_BUTTON = QCoreApplication.translate("ObjectView", "Export Data")
        self.DATA_EXPORT_NAME = QCoreApplication.translate("DataExportingWorker", "Name")
        self.DATA_EXPORT_INFRAME = QCoreApplication.translate("DataExportingWorker", "In-frame")
        self.DATA_EXPORT_TIMESPENT_AVG = QCoreApplication.translate("DataExportingWorker", "Time spent in average, (min)")
        self.DATA_EXPORT_TIMESPENT_TOT = QCoreApplication.translate("DataExportingWorker", "Time spent in total, (min)")
        self.DATA_EXPORT_NUMOFVISITORS = QCoreApplication.translate("DataExportingWorker", "Number of visitors, (persons)")
        self.DATA_EXPORT_DATES = QCoreApplication.translate("DataExportingWorker", "Dates")

        self.OBJECT_MODIFIER_DIALOG_TITLE = QCoreApplication.translate(
            "ObjectModifierDialog", "Object modification"
        )
        self.NAME_LABEL = QCoreApplication.translate("ObjectModifierDialog", "Name...")
        self.UPLOAD_BUTTON = QCoreApplication.translate(
            "ObjectModifierDialog", "Upload"
        )
        self.BACK_BUTTON = QCoreApplication.translate("ObjectModifierDialog", "Back")
        self.IN_FRAME_BUTTON = QCoreApplication.translate(
            "ObjectModifierDialog", "Add in-frame"
        )
        self.SHOW_BUTTON = QCoreApplication.translate("DatePickerDialog", "Show")


        self.OBJECT_LIST = QCoreApplication.translate("ObjectsContainer", "Objects")
        self.OBJECT_UPLOADER_DIALOG_TITLE = QCoreApplication.translate(
            "ObjectUploaderDialog", "New object upload"
        )
        self.STATUS_LABEL = QCoreApplication.translate(
            "ObjectUploaderDialog", "Nothing uploaded"
        )
        self.NEXT_BUTTON = QCoreApplication.translate("Global", "Next")
        self.CANCEL_BUTTON = QCoreApplication.translate("Global", "Cancel")
        self.STATUS_LABEL_UPDATED = QCoreApplication.translate(
            "ObjectUploaderDialog", "Uploaded file: "
        )
        self.FILE_UPLOAD_LABEL = QCoreApplication.translate(
            "FileUploadWidget", "Drag and drop a file here or click 'Browse' to select."
        )
