# This Python file uses the following encoding: utf-8
import os

from PySide2 import QtCore, QtMultimedia, QtMultimediaWidgets, QtWidgets

from data_model.project import load_project
from model_ui.segment_model import SegmentModel
from ui.generated.ui_mainwindow import Ui_Sentence
from worker import Worker, WorkerSignals


class MainWindow(Ui_Sentence, QtWidgets.QMainWindow):
    def __init__(self, project):
        QtWidgets.QMainWindow.__init__(self)
        Ui_Sentence.__init__(self)
        self.setupUi(self)

        self.actionOpen.triggered.connect(self.open)
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionSave.triggered.connect(self.save)
        self.actionQuit.triggered.connect(self.quit)

        self.player = QtMultimedia.QMediaPlayer()

        self.playlist = QtMultimedia.QMediaPlaylist(self.player)
        self.playlist.addMedia(QtCore.QUrl("file:/tmp/out.mp4"))

        self.videoWidget = QtMultimediaWidgets.QVideoWidget()
        self.player.setVideoOutput(self.videoWidget)
        self.player.setPlaylist(self.playlist)
        self.video_layout.addWidget(self.videoWidget)

        self.mapper = QtWidgets.QDataWidgetMapper()
        self.open_project(project)

        self.listView.indexesMoved.connect(self.table_index_change)
        self.listView.selectionChanged = self.table_index_change

        self.pushButton_add_sentence.clicked.connect(self.add_sentence)

        self.pushButton_sentence_edit.clicked.connect(self.edit_sentence)

        self.pushButton_compute.clicked.connect(self.compute_sentence)

        self.threadpool = QtCore.QThreadPool()

    def open_project(self, project):
        self.project = project
        self.segment_model = SegmentModel(project)
        self.listView.setModel(self.segment_model)

        self.mapper.clearMapping()
        self.mapper.setModel(self.segment_model)
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        self.mapper.addMapping(self.lineEdit_sentence, 0)
        self.mapper.addMapping(self.spinBox_index, 1)

    def add_sentence(self):
        self.setWindowModified(True)
        i = len(self.project.segments)
        self.segment_model.insertRow(i)

    def edit_sentence(self):
        self.mapper.submit()

    def table_index_change(self, selected, unselected):
        if len(selected.indexes()) > 0:
            self.mapper.setCurrentModelIndex(selected.indexes()[0])
        else:
            self.mapper.setCurrentIndex(-1)

    def compute_sentence(self):
        if not self.project.are_videos_ready():
            QtWidgets.QMessageBox.information(
                self,
                self.tr("ALERTE"),
                "Toutes les vidéos n'ont pas été téléchargées ?",
            )
        else:
            try:
                segment = self.get_selected_segment()

                def compute_done(combos):
                    segment.set_combos(combos)

                    QtWidgets.QMessageBox.information(
                        self, self.tr("ALERTE"), "Analyse terminée"
                    )

                worker = Worker(segment.analyze)
                worker.signals.result.connect(compute_done)
                self.threadpool.start(worker)

            except Exception as e:
                QtWidgets.QMessageBox.information(
                    self, self.tr("ALERTE"), str(e)
                )

    def get_selected_index(self):
        return self.listView.selectionModel().selectedIndexes()[0]

    def get_selected_segment(self):
        return self.segment_model.get_segment_from_index(
            self.get_selected_index()
        )

    def closeEvent(self, event):
        if self.wants_to_quit():
            event.accept()
        else:
            event.ignore()

    def open(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open p00p project"),
            None,
            self.tr("P00p project (*.p00p);;All Files (*)"),
        )
        try:
            self.open_project(load_project(path))
            self.setWindowModified(False)
        except EnvironmentError as e:
            QtWidgets.QMessageBox.information(
                self, self.tr("Unable to open file"), e.args[0]
            )

    def save(self):
        if self.isWindowModified():
            self._save()

    def _save(self):
        try:
            self.project.save()
            self.setWindowModified(False)
        except EnvironmentError as e:
            QtWidgets.QMessageBox.information(
                self, self.tr("Unable to open file"), e.args[0],
            )

    def save_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Save p00p project"),
            None,
            self.tr("P00p project (*.p00p);;All Files (*)"),
        )
        print(path)
        if path != "":
            self.project.set_path(path)
            self._save()

    def wants_to_quit(self):
        if self.isWindowModified():
            ret = QtWidgets.QMessageBox.warning(
                self,
                self.tr("Quit"),
                self.tr(
                    "The document has been modified.\nDo you want to save your changes?"
                ),
                QtWidgets.QMessageBox.Save
                | QtWidgets.QMessageBox.Discard
                | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Save,
            )
            if ret == QtWidgets.QMessageBox.Save:
                self.save()
            elif ret == QtWidgets.QMessageBox.Discard:
                pass
            elif ret == QtWidgets.QMessageBox.Cancel:
                return False
        return True

    def quit(self):
        if self.wants_to_quit():
            QtWidgets.QApplication.quit()
