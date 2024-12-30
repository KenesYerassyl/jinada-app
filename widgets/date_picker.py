from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QCalendarWidget,
    QPushButton,
    QDialogButtonBox,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
import datetime
from utils.constants import AppLabels
from paths import Paths


class DatePickerDialog(QDialog):

    date_picked = pyqtSignal(datetime.date, datetime.date)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())

        layout = QVBoxLayout()

        self.date_picker = RangeCalendar()

        labels_layout = QHBoxLayout()
        self.start_date_label = QLabel("...")
        self.start_date_label.setObjectName("DatePickerDialog-label")
        self.date_picker.set_start_date.connect(self.start_date_label.setText)
        self.end_date_label = QLabel("...")
        self.end_date_label.setObjectName("DatePickerDialog-label")
        self.date_picker.set_end_date.connect(self.end_date_label.setText)
        labels_layout.addWidget(self.start_date_label)
        labels_layout.addWidget(self.end_date_label)
        labels_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.show_button = QPushButton(AppLabels().SHOW_BUTTON)
        self.show_button.clicked.connect(self.on_show)
        self.show_button.setDisabled(True)
        self.show_button.setObjectName("dialog-button-positive")
        self.date_picker.date_selected.connect(self.show_button.setDisabled)

        self.cancel_button = QPushButton(AppLabels().CANCEL_BUTTON)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.cancel_button.setObjectName("dialog-button-negative")

        self.button_box = QDialogButtonBox(self)
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )
        self.button_box.addButton(
            self.show_button, QDialogButtonBox.ButtonRole.AcceptRole
        )

        layout.addWidget(self.date_picker)
        layout.addLayout(labels_layout)
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
    set_start_date = pyqtSignal(str)
    set_end_date = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.start_date: QDate = None
        self.end_date: QDate = None
        self.clicked.connect(self.date_is_clicked)
        self.setStyleSheet(f"""
            QCalendarWidget QWidget#qt_calendar_prevmonth {{
                qproperty-icon: url('{Paths.ARROW_LEFT_ICON}');
            }}

            QCalendarWidget QWidget#qt_calendar_nextmonth {{
                qproperty-icon: url('{Paths.ARROW_RIGHT_ICON}');
            }}
        """)

    def date_is_clicked(self, date):
        if self.start_date and self.end_date:
            self.start_date = None
            self.end_date = None

        if self.start_date is None:
            self.start_date = date
            self.end_date = None
            self.set_start_date.emit(date.toPyDate().strftime("%Y-%m-%d"))
        else:
            self.end_date = date
            if self.end_date < self.start_date:
                self.start_date, self.end_date = self.end_date, self.start_date
                self.set_start_date.emit(
                    self.start_date.toPyDate().strftime("%Y-%m-%d")
                )
            self.set_end_date.emit(self.end_date.toPyDate().strftime("%Y-%m-%d"))
        self.date_selected.emit(self.start_date is None or self.end_date is None)
