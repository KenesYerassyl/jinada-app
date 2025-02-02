from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PyQt6.QtGui import QColor

class ShadowedWidget(QWidget):

    def __init__(self):
        super().__init__()
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)  
        shadow.setOffset(2, 5)
        shadow.setColor(QColor(0, 0, 0, 160))

        self.setGraphicsEffect(shadow)