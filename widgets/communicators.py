from PyQt6.QtCore import QObject, pyqtSignal


class ObjectCommunicator(QObject):
    object_uploaded = pyqtSignal(str, str)
    object_modified = pyqtSignal(str, str, str, list, list)
    object_modification_cancelled = pyqtSignal()


class ObjectContainerCommunicator(QObject):
    item_clicked = pyqtSignal(int)
