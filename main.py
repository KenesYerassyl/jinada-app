# Python 3.10.11
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFileSystemWatcher, QTranslator, QCoreApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
import sys
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from db.object import Base
import paths

#TODO: Start processing videos, upon launching the app

def get_log_file_path() -> Path:
    """
    Determines the log file path based on the operating system.
    Creates necessary directories if they do not exist.
    """
    try:
        if sys.platform == "win32":
            base_dir = os.getenv("LOCALAPPDATA", Path.home())
        elif sys.platform == "darwin":
            base_dir = Path.home() / "Library/Logs"
        else:
            base_dir = Path.home() / ".local" / "share"

        log_dir = Path(base_dir) / "Jinada"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "application.log"
    except Exception as e:
        logging.error(f"Error getting log file path: {e}")
        raise

def setup_logging(disable: bool) -> None:
    """
    Sets up logging configuration for both file and console output.
    """
    if disable:
        logging.disable()
        return
    try:
        log_file = get_log_file_path()
        log_dir = os.path.dirname(log_file)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    except Exception as e:
        logging.error(f"Error setting up logging: {e}")
        raise


def setup_database() -> None:
    """
    Sets up the database and creates necessary directories.
    """
    try:
        os.makedirs(paths.SECURE_PATH, exist_ok=True)
        
        if not os.path.exists(paths.DB_PATH):
            os.makedirs(paths.Paths.OBJECT_FRAMES, exist_ok=True)
            os.makedirs(paths.Paths.RECORD_DATA_DIR, exist_ok=True)
        
            engine = create_engine(f"sqlite:///{paths.DB_PATH}", echo=True)
            Base.metadata.create_all(engine)
            logging.info(f"Database setup complete at {paths.DB_PATH}")
        else:
            logging.info(f"Database already exists at {paths.DB_PATH}")
    except Exception as e:
        logging.error(f"Error setting up database: {e}")
        raise


def setup_qss(app: QApplication) -> None:
    """
    Loads and applies QSS styles from file and sets variable replacements.
    """
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
        logging.info("QSS stylesheet applied successfully.")
    except Exception as e:
        logging.error(f"Error applying QSS stylesheet: {e}")
        raise

def setup_platform_specific_settings(app: QApplication) -> None:
    """
    Applies platform-specific settings, like window icons and app IDs for Windows.
    """
    try:
        if sys.platform == "win32":
            from ctypes import windll  # Only exists on Windows.
            myappid = 'com.yerassyl.Jinada'
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            logging.info("Windows-specific settings applied.")
            app.setWindowIcon(QIcon(paths.Paths.WINDOWS_ICON))
        elif sys.platform == "darwin":
            app.setWindowIcon(QIcon(paths.Paths.MACOSX_ICON))
    except Exception as e:
        logging.error(f"Error setting up platform-specific settings: {e}")
        raise

def main() -> None:
    """
    Main entry point of the application to set up the environment and run the app.
    """
    try:
        setup_logging(False)
        setup_database()
        app = QApplication(sys.argv)

        #Applying Translations (TODO: give an option to change the language, default will be ENG)
        translator = QTranslator(app)
        translator.load(paths.Paths.TRANSLATIONS_DIR)
        app.installTranslator(translator)

        setup_qss(app)

        watcher = QFileSystemWatcher([paths.Paths.QSS, paths.Paths.QSS_VARIABLES])
        watcher.fileChanged.connect(lambda: setup_qss(app))

        setup_platform_specific_settings(app)
        
        window = MainWindow()
        window.setWindowIcon(QIcon(paths.Paths.MACOSX_ICON))
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()