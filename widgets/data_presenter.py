from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QAbstractListModel
from datetime import date


class DataPresenterModel:

    def __init__(self, object_id: int, start_date: date, end_date: date):
        self.object_id = object_id
        self.start_date = start_date
        self.end_date = end_date


class DataPresenterWidget(QWidget):

    def __init__(self, object_id: int, start_date: date, end_date: date):
        super().__init__()
        self.model = DataPresenterModel(object_id, start_date, end_date)
