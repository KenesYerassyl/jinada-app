from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFileSystemWatcher, QTranslator, QCoreApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
import sys
import paths
from sqlalchemy import create_engine
from db.object import Base
import os

translate = QCoreApplication.translate


def apply_qss(app: QApplication):
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
        logging.debug(f"Error applying QSS: {e}")


def setup():
    try:
        logging.debug("Creating secured path dir")
        os.makedirs(paths.SECURE_PATH, exist_ok=True)
        if not os.path.exists(paths.DB_PATH):
            logging.debug("Setting up the local file system db")
            os.makedirs(paths.Paths.OBJECT_FRAMES, exist_ok=True)
            os.makedirs(paths.Paths.RECORD_DATA_DIR, exist_ok=True)
            logging.debug("Setting up the db itself")
            engine = create_engine(f"sqlite:///{paths.DB_PATH}", echo=True)
            Base.metadata.create_all(engine)
    except Exception as e:
        logging.debug(f"Error during setup: {e}")

from pathlib import Path

def get_log_file_path():
    logging.debug("Path for log file")
    # Cross-platform writable location
    if sys.platform == "win32":
        base_dir = os.getenv("LOCALAPPDATA", Path.home())
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library/Logs"  # macOS Logs directory
    else:
        base_dir = Path.home() / ".local" / "share"  # Linux equivalent

    log_dir = Path(base_dir) / "Jinada"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.debug(log_dir)
    return log_dir / "application.log"

import logging  
import os  
import sys  

# Define the logging configuration  
def setup_logging():  
    log_file = get_log_file_path()
    # Ensure the log directory exists  
    log_dir = os.path.dirname(log_file)  
    if not os.path.exists(log_dir) and log_dir != '':  
        os.makedirs(log_dir)  

    # Create a logger  
    logger = logging.getLogger()  
    logger.setLevel(logging.DEBUG)  # Set the logging level  

    # Define log format  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  

    # Create file handler  
    file_handler = logging.FileHandler(log_file)  
    file_handler.setFormatter(formatter)  
    logger.addHandler(file_handler)  

    # Create console handler  
    console_handler = logging.StreamHandler(sys.stdout)  
    console_handler.setFormatter(formatter)  
    logger.addHandler(console_handler)  


if __name__ == "__main__":
    try:
        setup_logging()
        setup()
        app = QApplication(sys.argv)

        """
            Applying Translations (TODO: give an option to change the language, default will be ENG)
        """
        logging.debug("Applying translator")
        translator = QTranslator(app)
        translator.load(paths.Paths.TRANSLATIONS_DIR)
        app.installTranslator(translator)
        logging.debug("Applying qss")
        apply_qss(app)
        watcher = QFileSystemWatcher([paths.Paths.QSS, paths.Paths.QSS_VARIABLES])
        def refresh_stylesheet():
            apply_qss(app)
        watcher.fileChanged.connect(refresh_stylesheet)
        logging.debug("let us see up to here!")
        window = MainWindow()
        window.setWindowIcon(QIcon(paths.Paths.MACOSX_ICON))
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.debug(e)
