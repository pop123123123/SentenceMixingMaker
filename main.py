# This Python file uses the following encoding: utf-8
import json
import sys

import sentence_mixing as sm
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication
from sentence_mixing.video_creator.download import dl_video

from data_model.project import Project
from view.MainWindow import MainWindow, load_project
from worker import Worker


def download_video_and_audio(urls):
    vid_paths = list(map(dl_video, urls))
    videos = sm.sentence_mixer.get_videos(urls)

    for video, path in zip(videos, vid_paths):
        n = len(video._base_path)
        assert path[:n] == video._base_path
        video.extension = path[n + 1 :]

    return videos


if __name__ == "__main__":
    app = QApplication([])

    vids = ["https://www.youtube.com/watch?v=_ZZ8oyZUGn8"]

    project = Project("/tmp/lol", 0, [vids],)

    config_path = "config.json"
    with open(config_path) as f:
        config = json.load(f)
    if "NODES" in config:
        sm.logic.parameters.NODES = config["NODES"]

    sm.sentence_mixer.prepare_sm_config_dict(config)

    worker = Worker(download_video_and_audio, vids)
    worker.signals.result.connect(project.set_videos)
    worker.signals.error.connect(print)

    threadpool = QtCore.QThreadPool()
    threadpool.start(worker)

    window = MainWindow(project)
    #    window.open_project(load_project('/tmp/lol.p00p'))
    window.show()

    sys.exit(app.exec_())
