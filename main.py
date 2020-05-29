# This Python file uses the following encoding: utf-8
import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from sentence_mixing import sentence_mixer
from sentence_mixing.video_creator.download import dl_video

from data_model.project import Project
from view.MainWindow import MainWindow
from worker import Worker


def download_video_and_audio(urls):
    vid_paths = list(map(dl_video, urls))
    videos = sentence_mixer.get_videos(urls)

    for video, path in zip(videos, vid_paths):
        n = len(video._base_path)
        assert path[:n] == video._base_path
        video.extension = path[n + 1 :]

    return videos


if __name__ == "__main__":
    app = QApplication([])

    vids = ["https://www.youtube.com/watch?v=_ZZ8oyZUGn8"]

    project = Project("/tmp/lol", 0, [vids],)

    sentence_mixer.prepare_sm(
        "/home/nicolas/Documents/Trucs/sentence_mixing_maker/config/config.json"
    )

    worker = Worker(download_video_and_audio, vids)
    worker.signals.result.connect(project.set_videos)
    worker.signals.error.connect(print)

    threadpool = QtCore.QThreadPool()
    threadpool.start(worker)

    window = MainWindow(project)
    window.show()

    window.player.play()

    sys.exit(app.exec_())
