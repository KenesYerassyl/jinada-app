from PyQt6.QtWidgets import (
    QMainWindow,
    QDockWidget,
)
from PyQt6.QtCore import QSize, QThreadPool, Qt
import utils.constants as constants
from widgets.object_view import ObjectView
from widgets.objects_container import ObjectsContainer
from local_db.db import get_object_by_id


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(1280, 720))
        self.setWindowTitle(constants.app_name)
        self.threadpool = QThreadPool()

        self.central_widget = ObjectView()
        self.setCentralWidget(self.central_widget)

        self.dock_widget = QDockWidget("Item list", self)
        self.dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dock_widget.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_widget)

        self.objects_container = ObjectsContainer()
        self.objects_container.communicator.item_clicked.connect(self.load_object_view)
        self.dock_widget.setWidget(self.objects_container)

    def load_object_view(self, object_id):
        self.central_widget.load_object(object_id)
