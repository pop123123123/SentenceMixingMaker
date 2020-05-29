# This Python file uses the following encoding: utf-8
import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from sentence_mixing import sentence_mixer

from data_model.project import Project
from view.MainWindow import MainWindow
from worker import Worker

if __name__ == "__main__":
    app = QApplication([])

    vids = ["https://www.youtube.com/watch?v=_ZZ8oyZUGn8"]

    project = Project(
        "/tmp/lol", 0, ["https://www.youtube.com/watch?v=_ZZ8oyZUGn8"]
    )

    sentence_mixer.prepare_sm(
        "/home/nicolas/Documents/Trucs/sentence_mixing_maker/config/config.json"
    )

    worker = Worker(sentence_mixer.get_videos, vids)
    worker.signals.result.connect(project.set_videos)

    threadpool = QtCore.QThreadPool()
    threadpool.start(worker)

    window = MainWindow(project)
    window.show()

    window.player.play()

    sys.exit(app.exec_())
