# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide2 import QtCore, QtGui, QtMultimedia, QtMultimediaWidgets, QtWidgets
from sentence_mixing.video_creator.video import create_video_file

import view.video_assembly as video_assembly
from data_model.project import Project, load_project
from model_ui.segment_model import SegmentModel
from ui.generated.ui_mainwindow import Ui_Sentence
from view import preview
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

        self.graphicsView = QtWidgets.QGraphicsView()
        self.video_layout.addWidget(self.graphicsView)
        self.graphicsView.setScene(QtWidgets.QGraphicsScene())
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.graphicsView.scene().addItem(self.pixmap)

        self.mapper = QtWidgets.QDataWidgetMapper()
        self.open_project(project)

        self.listView.indexesMoved.connect(self.table_index_change)
        self.listView.selectionChanged = self.table_index_change

        self.pushButton_add_sentence.clicked.connect(self.add_sentence)

        self.pushButton_sentence_edit.clicked.connect(self.edit_sentence)

        self.pushButton_compute.clicked.connect(self.compute_sentence)

        self.spinBox_index.valueChanged.connect(self.preview_combo)
        self.previewer = None
        self.previewers = {}
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
            return
        try:
            segment = self.get_selected_segment()
        except Exception as e:
            self.pop_error_box(str(e))
            return

        for k in list(self.previewers.keys()):
            if k[0] == segment:
                self.previewers.pop(k)

        def compute_done():
            self.pop_error_box("Analyse terminée")
            self.generate_combo_previews(segment, range(10))

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

    def preview_combo(self):
        if self.previewer is not None:
            self.previewer.stop()
        i = self.spinBox_index.value()
        seg = self.get_selected_segment()
        if (seg, i) not in self.previewers:
            self.generate_combo_previews(seg, [i], False)
            self.generate_combo_previews(seg, range(i + 1, i + 11))
        self.previewer = self.previewers[(seg, i)]
        self.previewer.run()

    def generate_combo_previews(self, segment, indices, use_worker=True):
        for i in indices:
            if (segment, i) in self.previewers:
                self.previewers[(segment, i)].stop()
        if use_worker:
            w = Worker(self._generate_combo_previews, segment, indices)
            w.signals.error.connect(print)
            self.threadpool.start(w)
        else:
            self._generate_combo_previews(segment, indices)

    def _generate_combo_previews(self, segment, indices):
        for i in indices:
            combo = segment.combos[i]
            self.previewers[(segment, i)] = preview.Previewer(
                combo, self.pixmap, self.graphicsView, True
            )
            print(f"generated {i}")

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

    def collect_combos(self, strict=True):
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

        # Retrieves phonems of all segments
        phonems = self.collect_combos(strict=True)

        # Progress bar dialog widget
        progress = video_assembly.VideoAssemblerProgressDialog(self)

        # Logging interface sending updates to progress bar (thread tolerant)
        logger = video_assembly.VideoAssemblerLogger(progress)

        # Thread executing video assembly
        worker = Worker(create_video_file, phonems, path, logger=logger)

        # Adding interruption system related to worker
        # When the user presses cancel button of the dialog, interruption boolean will be set to
        # True and video assembly will be canceled
        logger.set_interruption_callback(worker.should_be_interrupted)
        progress.canceled.connect(worker.interrupt)

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
