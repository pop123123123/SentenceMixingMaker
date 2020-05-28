# This Python file uses the following encoding: utf-8
import os

from PySide2 import QtCore, QtMultimedia, QtMultimediaWidgets, QtWidgets

from generated.ui_mainwindow import Ui_Sentence


class MainWindow(Ui_Sentence, QtWidgets.QMainWindow):
    def __init__(self, project):
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

        self.project = project
        self.listView.setModel(project.segment_model)

        self.listView.indexesMoved.connect(self.table_index_change)
        self.listView.selectionChanged = self.table_index_change

        self.pushButton_add_sentence.clicked.connect(self.add_sentence)

        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        self.mapper.setModel(project.segment_model)
        self.mapper.addMapping(self.lineEdit_sentence, 0)
        self.mapper.addMapping(self.spinBox_index, 1)

        self.pushButton_sentence_edit.clicked.connect(self.edit_sentence)

    def add_sentence(self):
        self.project.segment_model.insertRow(-1)

    def edit_sentence(self):
        self.mapper.submit()

    def table_index_change(self, selected, unselected):
        self.mapper.setCurrentModelIndex(selected.indexes()[0])

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