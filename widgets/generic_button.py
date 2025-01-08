from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon

class GenericButton(QPushButton):
    def __init__(self, icon_normal = None, icon_pressed = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if icon_normal is not None and icon_pressed is not None:
            self.icon_normal = QIcon(icon_normal)
            self.icon_pressed = QIcon(icon_pressed)
            self.setIcon(self.icon_normal)

    def mousePressEvent(self, event):
        if self.icon_pressed is not None:
            self.setIcon(self.icon_pressed)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.icon_normal is not None:
            self.setIcon(self.icon_normal)
        super().mouseReleaseEvent(event)