from PyQt6.QtCore import QObject, pyqtSignal
from local_db.object import Object, ObjectRecord


class ObjectCommunicator(QObject):
    object_uploaded = pyqtSignal(Object, ObjectRecord)
    object_modified = pyqtSignal(Object, ObjectRecord)
    object_modification_cancelled = pyqtSignal(Object, ObjectRecord)


class ObjectContainerCommunicator(QObject):
    item_clicked = pyqtSignal(int)
