# This Python file uses the following encoding: utf-8
import os
import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QAction, QApplication, QFileDialog

window = None
saved = False
changed = False


def open():
    fileName = QFileDialog.getOpenFileName(
        window,
        window.tr("Open p00p project"),
        None,
        window.tr("P00p project (*.p00p);;All Files (*)"),
    )
    print("open", fileName)


def save():
    global saved, changed
    if not saved:
        save_as()
        saved = True
    elif changed:
        # save
        changed = False


def save_as():
    global changed
    fileName = QFileDialog.getSaveFileName(
        window,
        window.tr("Save p00p project"),
        None,
        window.tr("P00p project (*.p00p);;All Files (*)"),
    )
    changed = False
    print("open", fileName)


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

    open_action = window.findChild(QAction, "actionOpen")
    open_action.triggered.connect(open)
    save_as_action = window.findChild(QAction, "actionSave_as")
    save_as_action.triggered.connect(save_as)
    save_as_action = window.findChild(QAction, "actionSave")
    save_as_action.triggered.connect(save)
    window.show()

    sys.exit(app.exec_())
