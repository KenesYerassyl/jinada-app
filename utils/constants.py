from PyQt6.QtCore import QCoreApplication
import os

# TODO add try except blocks

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
        self.ERROR_DURING_UPLOAD = QCoreApplication.translate(
            "ObjectUploaderDialog", "Error during uploding"
        )

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
        self.MODIFY_FRAMES_BUTTON = QCoreApplication.translate(
            "ObjectView", "Modify Frames"
        )
        self.DATE_PICKER_BUTTON = QCoreApplication.translate(
            "ObjectView", "Export Data"
        )
        self.OBJECT_MODIFIER_DIALOG_TITLE = QCoreApplication.translate(
            "ObjectModifierDialog", "Object modification"
        )
        self.NAME_LABEL = QCoreApplication.translate("ObjectModifierDialog", "Name...")
        self.UPLOAD_BUTTON = QCoreApplication.translate(
            "ObjectModifierDialog", "Upload"
        )
        self.BACK_BUTTON = QCoreApplication.translate("ObjectModifierDialog", "Back")
        self.OUT_FRAME_BUTTON = QCoreApplication.translate(
            "ObjectModifierDialog", "Add out-frame"
        )
        self.IN_FRAME_BUTTON = QCoreApplication.translate(
            "ObjectModifierDialog", "Add in-frame"
        )
        self.SHOW_BUTTON = QCoreApplication.translate("DatePickerDialog", "Show")

        self.BAR_GRAPH1 = QCoreApplication.translate(
            "DataPresenterWidget", "Total number of visitors on each Exhibit"
        )
        self.BAR_GRAPH2 = QCoreApplication.translate(
            "DataPresenterWidget", "Average number of visitors on each Exhibit"
        )
        self.BAR_GRAPH3 = QCoreApplication.translate(
            "DataPresenterWidget", "Average time spent on each Exhibit"
        )

        self.BAR_GRAPH_VISITORS_YLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Number of visitors"
        )
        self.BAR_GRAPH_TIME_YLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Average Time (min)"
        )
        self.BAR_GRAPH_XLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Exhibits"
        )

        self.LINE_GRAPH1 = QCoreApplication.translate(
            "DataPresenterWidget", "Change of total number of visitors on each Exhibit"
        )
        self.LINE_GRAPH2 = QCoreApplication.translate(
            "DataPresenterWidget", "Change of average number of visitors on each Exhibit"
        )
        self.LINE_GRAPH3 = QCoreApplication.translate(
            "DataPresenterWidget", "Change of average time spent on each Exhibit"
        )

        self.LINE_GRAPH_TIME_YLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Average Time (min)"
        )
        self.LINE_GRAPH_VISITORS_YLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Number of Visitors"
        )
        self.LINE_GRAPH_XLABEL = QCoreApplication.translate(
            "DataPresenterWidget", "Selected time period"
        )

        self.EXHIBIT = QCoreApplication.translate("DataPresenterWidget", "Exhibit")
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
