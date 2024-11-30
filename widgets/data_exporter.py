from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QCalendarWidget,
    QPushButton,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QTextCharFormat
import datetime


class DataExporterDialog(QDialog):

    date_picked = pyqtSignal(datetime.date, datetime.date)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())

        layout = QVBoxLayout()

        self.date_picker = RangeCalendar()

        self.show_button = QPushButton("Show")
        self.show_button.clicked.connect(self.on_show)
        self.show_button.setDisabled(True)
        self.date_picker.date_selected.connect(self.show_button.setDisabled)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

        self.button_box = QDialogButtonBox(self)
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )
        self.button_box.addButton(
            self.show_button, QDialogButtonBox.ButtonRole.AcceptRole
        )

        layout.addWidget(self.date_picker)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def on_show(self):
        self.date_picked.emit(
            self.date_picker.start_date.toPyDate(), self.date_picker.end_date.toPyDate()
        )
        self.accept()

    def on_cancel(self):
        self.reject()


class RangeCalendar(QCalendarWidget):

    date_selected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.start_date: QDate = None
        self.end_date: QDate = None
        self.clicked.connect(self.date_is_clicked)

    def date_is_clicked(self, date):
        if self.start_date and self.end_date:
            self._highlight_range(self.start_date, self.end_date, False)
            self.start_date = None
            self.end_date = None
        if self.start_date is None:
            self.start_date = date
            self.end_date = None
            self.setDateTextFormat(self.start_date, self._highlight_format(True))
        else:
            self.end_date = date
            if self.end_date < self.start_date:
                self.start_date, self.end_date = self.end_date, self.start_date
            self._highlight_range(self.start_date, self.end_date, True)

        self.date_selected.emit(self.start_date is None or self.end_date is None)

    def _highlight_format(self, flag: bool):
        fmt = QTextCharFormat()
        if flag:
            fmt.setBackground(Qt.GlobalColor.lightGray)
        return fmt

    def _highlight_range(self, start, end, flag):
        current_date = start
        while current_date <= end:
            self.setDateTextFormat(current_date, self._highlight_format(flag))
            current_date = current_date.addDays(1)
