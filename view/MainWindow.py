# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide2 import QtCore, QtMultimedia, QtMultimediaWidgets, QtWidgets
from sentence_mixing.video_creator.video import create_video_file

import view.video_assembly as video_assembly
from data_model.project import Project, load_project
from model_ui.segment_model import SegmentModel
from ui.generated.ui_mainwindow import Ui_Sentence
from view.NewProjectDialog import NewProjectDialog
from worker import AnalyzeWorker, Worker, WorkerSignals


class MainWindow(Ui_Sentence, QtWidgets.QMainWindow):
    def __init__(self, project):
        QtWidgets.QMainWindow.__init__(self)
        Ui_Sentence.__init__(self)
        self.setupUi(self)

        self.actionNew.triggered.connect(self.new)
        self.actionOpen.triggered.connect(self.open)
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionSave.triggered.connect(self.save)
        self.actionExport.triggered.connect(self.export)
        self.actionQuit.triggered.connect(self.quit)

        self.player = QtMultimedia.QMediaPlayer()

        self.playlist = QtMultimedia.QMediaPlaylist(self.player)
        self.playlist.setPlaybackMode(self.playlist.Loop)

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

        self.spinBox_index.valueChanged.connect(self.generate_combo_preview)

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

        index = self.segment_model.createIndex(i, 0)
        self.listView.setCurrentIndex(index)

    def edit_sentence(self):
        self.mapper.submit()

    def table_index_change(self, selected, unselected):
        if len(selected.indexes()) > 0:
            self.mapper.setCurrentModelIndex(selected.indexes()[0])
        else:
            self.mapper.setCurrentIndex(-1)

    def pop_error_box(self, message):
        print(message)
        QtWidgets.QMessageBox.information(
            self, self.tr("ALERTE"), message,
        )

    def compute_sentence(self):
        if not self.project.are_videos_ready():
            self.pop_error_box(
                "Toutes les vidéos n'ont pas été téléchargées ?"
            )
        else:
            try:
                segment = self.get_selected_segment()
            except Exception as e:
                self.pop_error_box(str(e))

            def compute_done():
                self.pop_error_box("Analyse terminée")

            worker = AnalyzeWorker(segment)
            worker.signals.finished.connect(compute_done)
            worker.signals.error.connect(self.pop_error_box)
            self.threadpool.start(worker)

    def get_selected_index(self):
        return self.listView.selectionModel().selectedIndexes()[0]

    def get_selected_segment(self):
        return self.segment_model.get_segment_from_index(
            self.get_selected_index()
        )

    def play_combo_preview(self, _):
        path = os.path.abspath("out.mp4")
        url = QtCore.QUrl("file://" + path)

        self.playlist.clear()
        self.playlist.addMedia(url)
        self.player.play()

    def generate_combo_preview(self):
        self.playlist.clear()

        segment = self.get_selected_segment()
        combo = segment.combos[self.spinBox_index.value()]
        phonems = combo.get_audio_phonems()

        worker = Worker(create_video_file, phonems, "out.mp4")
        worker.signals.result.connect(self.play_combo_preview)
        self.threadpool.start(worker)

    def closeEvent(self, event):
        if self.wants_to_quit():
            event.accept()
        else:
            event.ignore()

    def new(self):
        findDialog = NewProjectDialog(self)
        seed, urls = findDialog.get_project_settings()
        self.open_project(Project(None, seed, urls))
        self.setWindowModified(False)

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
        if self.project.path is None:
            self.save_as()
        elif self.isWindowModified():
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

    def collect_combos(self, strict):
        if strict and not self.project.segments:
            raise Exception("No segment found")

        phonems = []
        for segment in self.project.segments:
            if not segment.combos:
                if strict:
                    raise Exception("A segment have not been analyzed")
            else:
                combo = segment.get_chosen_combo()
                phonems.extend(combo.get_audio_phonems())

        return phonems

    def export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Export p00p project"),
            None,
            self.tr("mp4 video (*.mp4);;All Files (*)"),
        )

        if path == "":
            self.pop_error_box("Path is empty")
            return

        if Path(path).suffix != ".mp4":
            self.pop_error_box("Exported file must have '.mp4' extension")
            return

        phonems = self.collect_combos(True)

        progress = video_assembly.VideoAssemblerProgressDialog(self)
        logger = video_assembly.VideoAssemblerLogger(progress)
        worker = Worker(create_video_file, phonems, path, logger=logger)

        progress.open()

        worker.signals.finished.connect(progress.close)
        worker.signals.error.connect(self.pop_error_box)
        self.threadpool.start(worker)

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
