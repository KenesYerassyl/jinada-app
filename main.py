from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFileSystemWatcher, QTranslator, QCoreApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
import sys
import paths
from sqlalchemy import create_engine
from db.object import Base
import os
from pathlib import Path
import logging

translate = QCoreApplication.translate

def get_log_file_path():
    if sys.platform == "win32":
        base_dir = os.getenv("LOCALAPPDATA", Path.home())
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library/Logs"
    else:
        base_dir = Path.home() / ".local" / "share"

    log_dir = Path(base_dir) / "Jinada"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "application.log"

def setup_logging():  
    log_file = get_log_file_path()
    log_dir = os.path.dirname(log_file)  
    if not os.path.exists(log_dir) and log_dir != '':  
        os.makedirs(log_dir)  

    logger = logging.getLogger()  
    logger.setLevel(logging.DEBUG) 

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  

    file_handler = logging.FileHandler(log_file)  
    file_handler.setFormatter(formatter)  
    logger.addHandler(file_handler)  

    console_handler = logging.StreamHandler(sys.stdout)  
    console_handler.setFormatter(formatter)  
    logger.addHandler(console_handler)  


def setup_database():
    try:
        os.makedirs(paths.SECURE_PATH, exist_ok=True)
        if not os.path.exists(paths.DB_PATH):
            os.makedirs(paths.Paths.OBJECT_FRAMES, exist_ok=True)
            os.makedirs(paths.Paths.RECORD_DATA_DIR, exist_ok=True)
            engine = create_engine(f"sqlite:///{paths.DB_PATH}", echo=True)
            Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error during setup: {e}")


def setup_qss(app: QApplication):
    try:
        variables = {}
        with open(paths.Paths.QSS_VARIABLES, "r") as vf:
            for line in vf:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    variables[key.strip()] = value.strip()

        with open(paths.Paths.QSS, "r") as qf:
            qss = qf.read()
            for key, value in variables.items():
                qss = qss.replace(key, value)

        app.setStyleSheet(qss)
    except Exception as e:
        logging.error(f"Error applying QSS: {e}")

def setup_platform_specific_settings(app: QApplication):
    if sys.platform == "win32":
        try:
            from ctypes import windll  # Only exists on Windows.
            myappid = 'com.yerassyl.Jinada'
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except ImportError:
            logging.error(f"Error setting up Windows specific settings: {e}")
        app.setWindowIcon(QIcon(paths.Paths.WINDOWS_ICON))

if __name__ == "__main__":
    try:
        setup_logging()
        setup_database()
        app = QApplication(sys.argv)

        """
            Applying Translations (TODO: give an option to change the language, default will be ENG)
        """
        translator = QTranslator(app)
        translator.load(paths.Paths.TRANSLATIONS_DIR)
        app.installTranslator(translator)

        setup_qss(app)
        watcher = QFileSystemWatcher([paths.Paths.QSS, paths.Paths.QSS_VARIABLES])
        def refresh_stylesheet():
            setup_qss(app)
        watcher.fileChanged.connect(refresh_stylesheet)

        setup_platform_specific_settings(app)

        window = MainWindow()
        window.setWindowIcon(QIcon(paths.Paths.MACOSX_ICON))
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error un running the app: {e}")
