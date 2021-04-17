# This Python file uses the following encoding: utf-8
import json
import sys

import sentence_mixing as sm
from PySide2.QtWidgets import QApplication

from view.MainWindow import MainWindow, load_project


if __name__ == "__main__":
    app = QApplication([])

    config_path = "config.json"
    with open(config_path) as f:
        config = json.load(f)
    if "NODES" in config:
        sm.logic.parameters.NODES = config["NODES"]

    sm.sentence_mixer.prepare_sm_config_dict(config)

    window = None
    if len(sys.argv) > 1:
        window = MainWindow(load_project(sys.argv[1]))
    else:
        window = MainWindow.fromNew()
    if window is not None:
        window.show()

    sys.exit(app.exec_())
