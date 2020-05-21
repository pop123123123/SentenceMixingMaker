# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtWidgets import QApplication

from view.MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    window.player.play()

    sys.exit(app.exec_())
