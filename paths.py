import os
import sys
from PyQt6.QtCore import QStandardPaths

BASEDIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(".")
RESOURCES = "resources"
MODELS = "models"
ICONS = "icons"
RECORD_DATA = "record_data"
TRANSLATIONS = "translations"
SECURE_PATH = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), ".myappdata")  # Hidden folder
DB_PATH = os.path.join(SECURE_PATH, "objects.db")


class Paths:
    QSS = os.path.join(BASEDIR, RESOURCES, "style.qss")
    QSS_VARIABLES = os.path.join(BASEDIR, RESOURCES, "variables.txt")
    MACOSX_ICON = os.path.join(BASEDIR, RESOURCES, "icon_macosx.icns")
    WINDOWS_ICON = os.path.join(BASEDIR, RESOURCES, "icon_windows.ico")
    MOVE_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "move.svg")
    CONFIRM_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "confirm.svg")
    REJECT_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "reject.svg")
    TRASH_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "trash.svg")
    FILE_PLUS_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "file-plus.svg")
    PLUS_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "plus.svg")
    PLUS_CLICKED_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "plus_clicked.svg")
    ARROW_LEFT_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "arrow_left.svg")
    ARROW_RIGHT_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "arrow_right.svg")
    TRANSLATIONS_DIR = os.path.join(BASEDIR, RESOURCES, TRANSLATIONS, "app_ru.qm")
    ENCODER_MODEL_FILE = os.path.join(BASEDIR, MODELS, "mars-small128.pb")
    YOLO_MODEL_PATH = os.path.join(BASEDIR, MODELS, "yolo11m70.pt")
    OBJECT_FRAMES = os.path.join(SECURE_PATH, "object_frame")
    RECORD_DATA_DIR = os.path.join(SECURE_PATH, RECORD_DATA)


    def record_data_npz(record_id):
        return os.path.join(SECURE_PATH, RECORD_DATA, f"{record_id}.npz")

    def record_data(record_id):
        return os.path.join(SECURE_PATH, RECORD_DATA, f"{record_id}")

