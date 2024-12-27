import os
import sys

BASEDIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(".")
RESOURCES = "resources"
MODELS = "models"
ICONS = "icons"
LOCAL_DB = "local_db"
RECORD_DATA = "record_data"
TRANSLATIONS = "translations"


class Paths:
    QSS = os.path.join(BASEDIR, RESOURCES, "style.qss")
    QSS_VARIABLES = os.path.join(BASEDIR, RESOURCES, "variables.txt")
    MOVE_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "move.svg")
    CONFIRM_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "confirm.svg")
    REJECT_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "reject.svg")
    TRASH_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "trash.svg")
    FILE_PLUS_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "file-plus.svg")
    PLUS_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "plus.svg")
    PLUS_CLICKED_ICON = os.path.join(BASEDIR, RESOURCES, ICONS, "plus_clicked.svg")
    ENCODER_MODEL_FILE = os.path.join(BASEDIR, MODELS, "mars-small128.pb")
    YOLO_MODEL_PATH = os.path.join(BASEDIR, MODELS, "yolov10b.pt")
    OBJECT_FRAMES = os.path.join(BASEDIR, LOCAL_DB, "object_frame")
    RECORD_DATA_DIR = os.path.join(BASEDIR, LOCAL_DB, RECORD_DATA)
    TRANSLATIONS_DIR = os.path.join(BASEDIR, RESOURCES, TRANSLATIONS, "app_ru.qm")

    def record_data_npz(record_id):
        return os.path.join(BASEDIR, LOCAL_DB, RECORD_DATA, f"{record_id}.npz")

    def record_data(record_id):
        return os.path.join(BASEDIR, LOCAL_DB, RECORD_DATA, f"{record_id}")

