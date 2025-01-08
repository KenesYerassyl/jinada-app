from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsDropShadowEffect, QWidget
from utils.constants import STANDARD_WIDTH


def rescale_pixmap(pixmap: QPixmap, target_width=STANDARD_WIDTH) -> QPixmap:
    if pixmap.isNull():
        raise ValueError("Invalid QPixmap: Pixmap is null.")
    if pixmap.width() == 0:
        raise ValueError("Invalid pixmap. Width is zero.")
    aspect_ratio = pixmap.height() / pixmap.width()
    target_height = int(target_width * aspect_ratio)
    return pixmap.scaled(
        target_width,
        target_height,
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )


def copy_ellipse_item(original_item: QGraphicsEllipseItem) -> QGraphicsEllipseItem:
    """
    Create a copy of a QGraphicsEllipseItem, duplicating its geometry and appearance.

    Note: This does not copy parent-child relationships or custom data.
    """
    new_item = QGraphicsEllipseItem(original_item.rect())
    new_item.setPen(original_item.pen())
    new_item.setBrush(original_item.brush())
    new_item.setPos(original_item.pos())
    new_item.setRotation(original_item.rotation())
    new_item.setTransform(original_item.transform())
    new_item.setZValue(original_item.zValue())
    new_item.setVisible(original_item.isVisible())  # Optional: Copy visibility
    return new_item


def copy_line_item(original_item: QGraphicsLineItem) -> QGraphicsLineItem:
    """
    Create a copy of a QGraphicsLineItem, duplicating its geometry and appearance.

    Note: This does not copy parent-child relationships or custom data.
    """
    new_item = QGraphicsLineItem(original_item.line())
    new_item.setPen(original_item.pen())
    new_item.setPos(original_item.pos())
    new_item.setRotation(original_item.rotation())
    new_item.setTransform(original_item.transform())
    new_item.setZValue(original_item.zValue())
    new_item.setVisible(original_item.isVisible())  # Optional: Copy visibility
    return new_item