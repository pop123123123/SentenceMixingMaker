# This Python file uses the following encoding: utf-8
import sys
import traceback

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from sentence_mixing import sentence_mixer

from data_model.project import Project
from view.MainWindow import MainWindow


class WorkerSignals(QtCore.QObject):
    finished = QtCore.Signal()
    error = QtCore.Signal(str)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(int)


class Downloader(QtCore.QRunnable):
    def __init__(self, video_urls):
        super(Downloader, self).__init__()
        self.video_urls = video_urls
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            result = sentence_mixer.get_videos(self.video_urls)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.result.emit(
                result
            )  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


if __name__ == "__main__":
    app = QApplication([])

    vids = ["https://www.youtube.com/watch?v=_ZZ8oyZUGn8"]

    project = Project("yo", 0)

    def print_output(videos):
        project.set_videos(videos)

    def thread_complete():
        print("finished")

    def progress_fn(n):
        print("%d%% done" % n)

    threadpool = QtCore.QThreadPool()
    worker = Downloader(
        vids
    )  # Any other args, kwargs are passed to the run function
    worker.signals.result.connect(print_output)
    worker.signals.finished.connect(thread_complete)
    worker.signals.progress.connect(progress_fn)
    threadpool.start(worker)

    sentence_mixer.prepare_sm(
        "/home/nicolas/Documents/Trucs/sentence_mixing_maker/config/config.json"
    )

    window = MainWindow(project)
    window.show()

    window.player.play()

    sys.exit(app.exec_())
