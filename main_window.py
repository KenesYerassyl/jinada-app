from PyQt6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QWidget
)
from PyQt6.QtCore import QSize, Qt
import utils.constants as constants
from widgets.object_view import ObjectView
from widgets.objects_container import ObjectsContainer
import logging


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(1280, 720))
        self.setWindowTitle(constants.APP_NAME)
        self.setContentsMargins(15, 15, 15, 15)

        self.central_widget = ObjectView()
        self.setCentralWidget(self.central_widget)

        self.dock_widget = QDockWidget(self)
        self.dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.dock_widget.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_widget)

        self.objects_container = ObjectsContainer()
        self.objects_container.item_clicked.connect(self.load_object_view)
        self.objects_container.list.object_deleted.connect(self.central_widget.reset)
        self.dock_widget.setWidget(self.objects_container)

    def load_object_view(self, object_id: int):
        if object_id is None:
            logging.error(f"Error: Invalid object ID: {object_id}")
            return
        self.central_widget.load_object(object_id)
