# This Python file uses the following encoding: utf-8
import os

from PySide2 import QtCore, QtMultimedia, QtMultimediaWidgets, QtWidgets

from generated.ui_mainwindow import Ui_Sentence


class MainWindow(Ui_Sentence, QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_Sentence.__init__(self)
        self.setupUi(self)

        self.actionOpen.triggered.connect(self.open)
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionSave.triggered.connect(self.save)

        self.player = QtMultimedia.QMediaPlayer()

        self.playlist = QtMultimedia.QMediaPlaylist(self.player)
        self.playlist.addMedia(QtCore.QUrl("file:/tmp/out.mp4"))

        self.videoWidget = QtMultimediaWidgets.QVideoWidget()
        self.player.setVideoOutput(self.videoWidget)
        self.player.setPlaylist(self.playlist)
        self.video_layout.addWidget(self.videoWidget)

        self.saved = False
        self.changed = False

    def open(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open p00p project"),
            None,
            self.tr("P00p project (*.p00p);;All Files (*)"),
        )
        print("open", fileName)

    def save(self):
        if not self.saved:
            self.save_as()
            self.saved = True
        elif changed:
            # save
            self.changed = False

    def save_as(self):
        global changed
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Save p00p project"),
            None,
            self.tr("P00p project (*.p00p);;All Files (*)"),
        )
        self.changed = False
        print("open", fileName)
