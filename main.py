from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFileSystemWatcher, QTranslator, QLocale
from main_window import MainWindow
from PyQt6.QtCore import QCoreApplication
import sys
import os
from paths import Paths

translate = QCoreApplication.translate


def apply_qss(app: QApplication):
    try:
        variables = {}
        with open(Paths.QSS_VARIABLES, "r") as vf:
            for line in vf:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    variables[key.strip()] = value.strip()

        with open(Paths.QSS, "r") as qf:
            qss = qf.read()
            for key, value in variables.items():
                qss = qss.replace(key, value)

        app.setStyleSheet(qss)
    except Exception as e:
        print(f"Error applying QSS: {e}")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    translator = QTranslator(app)

    translator.load(Paths.TRANSLATIONS_DIR)
    app.installTranslator(translator)
    apply_qss(app)

    watcher = QFileSystemWatcher([Paths.QSS, Paths.QSS_VARIABLES])

    def refresh_stylesheet():
        apply_qss(app)

    watcher.fileChanged.connect(refresh_stylesheet)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
