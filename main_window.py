from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
)
from PyQt6.QtCore import QSize, QThreadPool, Qt
import sys
import utils.constants as constants
from widgets.object_view import ObjectView
from widgets.objects_container import ObjectsContainer


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
        self.objects_container.list.addItems(["Video 1", "Video 2", "Video 3"])
        self.dock_widget.setWidget(self.objects_container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())