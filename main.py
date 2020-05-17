# This Python file uses the following encoding: utf-8
import os
import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    app = QApplication([])

    ui_file_name = "mainwindow.ui"
    path = os.path.join(os.path.dirname(__file__), ui_file_name)
    ui_file = QFile(path)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(path, ui_file.errorString()))
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.show()

    sys.exit(app.exec_())
