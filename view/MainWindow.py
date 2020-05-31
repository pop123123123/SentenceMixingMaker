# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide2 import QtCore, QtGui, QtMultimedia, QtMultimediaWidgets, QtWidgets
from sentence_mixing.video_creator.video import create_video_file

import view.video_assembly as video_assembly
from data_model.project import Project, load_project
from data_model.segment import AnalysisState
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

        # self.listView.indexesMoved.connect(self.table_index_change)
        self.listView.selectionChanged = self.table_index_change

        self.pushButton_add_sentence.clicked.connect(self.add_sentence)

        self.pushButton_sentence_edit.clicked.connect(self.edit_sentence)

        self.pushButton_compute.clicked.connect(self.compute_sentence)

        self.spinBox_index.valueChanged.connect(self.preview_combo)
        self.previewer = None
        self.threadpool = QtCore.QThreadPool()

        # Change buttons when data changed or new segment selected
        self.mapper.currentIndexChanged.connect(self.update_buttons)
        self.segment_model.dataChanged.connect(self.update_buttons)

    def open_project(self, project):
        self.project = project
        self.segment_model = SegmentModel(project)
        self.listView.setModel(self.segment_model)

        self.mapper.clearMapping()
        self.mapper.setModel(self.segment_model)
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        self.mapper.addMapping(self.lineEdit_sentence, 0)
        self.mapper.addMapping(self.spinBox_index, 1)

    def update_buttons(self, *args):
        selected_segment = self.get_selected_segment()

        if (
            selected_segment
            and selected_segment.analysis_state == AnalysisState.NEED_ANALYSIS
        ):
            self.pushButton_compute.setEnabled(True)
        else:
            self.pushButton_compute.setEnabled(False)

    def add_sentence(self):
        self.setWindowModified(True)
        i = len(self.project.segments)
        self.segment_model.insertRow(i)

        index = self.segment_model.createIndex(i, 0)
        self.listView.setCurrentIndex(index)

    def set_analysis_state_from_row_index(self, index, state):
        index_column_analysis = index.sibling(index.row(), 2)
        self.segment_model.setData(
            index_column_analysis, state, QtCore.Qt.EditRole
        )

    def edit_sentence(self):
        self.mapper.submit()

        self.set_analysis_state_from_row_index(
            self.get_selected_index(), AnalysisState.NEED_ANALYSIS
        )

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
            index = self.get_selected_index()
            segment = self.get_selected_segment()
        except Exception as e:
            self.pop_error_box(str(e))
            return

        if self.previewer is not None:
            self.previewer.stop()
        preview.previewManager.cancel(segment)

        def compute_done(_):
            preview.previewManager.compute_previews(
                self.threadpool, segment.combos[:10]
            )
            self.set_analysis_state_from_row_index(
                index, AnalysisState.ANALYZED
            )

        def compute_error(err):
            self.set_analysis_state_from_row_index(
                index, AnalysisState.NEED_ANALYSIS
            )
            self.pop_error_box(err)

        self.set_analysis_state_from_row_index(index, AnalysisState.ANALYZING)

        worker = AnalyzeWorker(segment)
        worker.signals.result.connect(compute_done)
        worker.signals.error.connect(compute_error)
        self.threadpool.start(worker)

    def get_selected_index(self):
        return self.listView.selectionModel().selectedIndexes()[0]

    def get_selected_segment(self):
        return self.segment_model.get_segment_from_index(
            self.get_selected_index()
        )

    def preview_combo(self, i):
        if self.previewer is not None:
            self.previewer.stop()
        segment = self.get_selected_segment()
        self.previewer = preview.previewManager.get_preview(segment.combos[i])
        preview.previewManager.compute_previews(
            self.threadpool, segment.combos[i + 1 : i + 6]
        )
        self.previewer.run(self.pixmap, self.graphicsView, True)

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
