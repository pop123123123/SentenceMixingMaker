# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide2 import QtCore, QtGui, QtMultimedia, QtMultimediaWidgets, QtWidgets
from sentence_mixing.video_creator.video import create_video_file

import view.commands as commands
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

        self.actionUndo.triggered.connect(
            self.segment_model.command_stack.undo
        )
        self.actionRedo.triggered.connect(
            self.segment_model.command_stack.redo
        )

        self.segment_model.command_stack.canUndoChanged.connect(
            self.actionUndo.setEnabled
        )
        self.segment_model.command_stack.canRedoChanged.connect(
            self.actionRedo.setEnabled
        )
        self.segment_model.command_stack.cleanChanged.connect(
            self.stackCleanChanged
        )

        # self.listView.indexesMoved.connect(self.table_index_change)
        self.listView.currentChanged = self.table_index_change
        self.segment_model.dataChanged.connect(self.data_changed)

        self.pushButton_add_sentence.clicked.connect(self.add_sentence)
        self.pushButton_remove_sentence.clicked.connect(self.remove_sentence)

        self.spinBox_index.valueChanged.connect(self.preview_combo)
        self.previewer = None
        self.threadpool = QtCore.QThreadPool()

        self.analyze_worker_list = []

        self.show_warning_message = True

    def open_project(self, project):
        self.project = project
        self.segment_model = SegmentModel(project)
        self.listView.setModel(self.segment_model)

        self.mapper.clearMapping()
        self.mapper.setModel(self.segment_model)
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.AutoSubmit)
        self.mapper.addMapping(self.spinBox_index, 1)

    @QtCore.Slot()
    def stackCleanChanged(self, is_clean):
        self.setWindowModified(not is_clean)

    def add_sentence(self):
        i = self.get_selected_i()
        command = commands.AddSegmentCommand(
            self.segment_model, self.listView, i, i + 1
        )
        self.segment_model.command_stack.push(command)

    def remove_sentence(self):
        i = self.get_selected_i()
        command = commands.RemoveSegmentCommand(
            self.segment_model, self.listView, i
        )
        self.segment_model.command_stack.push(command)

    def table_index_change(self, current, _previous):
        self.mapper.setCurrentIndex(current.row())
        preview.previewManager.cancel(
            self.segment_model.get_segment_from_index(_previous)
        )

        if current.row() == -1:
            self.pushButton_remove_sentence.setDisabled(True)
            self.spinBox_index.setDisabled(True)
        else:
            self.pushButton_remove_sentence.setDisabled(False)
            self.spinBox_index.setDisabled(False)

    def pop_error_box(self, message):
        print(message)
        QtWidgets.QMessageBox.information(
            self, self.tr("ALERTE"), message,
        )

    def pop_warning_box(self, message):
        if self.show_warning_message:

            def check_changed(state):
                # Checked
                if state == 2:
                    self.show_warning_message = False
                else:
                    self.show_warning_message = True

            warning_box = QtWidgets.QMessageBox(self)
            warning_box.setText(message)
            warning_box.setIcon(QtWidgets.QMessageBox.Warning)
            warning_box.addButton(QtWidgets.QMessageBox.Ok)
            warning_box.setDefaultButton(QtWidgets.QMessageBox.Ok)

            cb = QtWidgets.QCheckBox(
                "Ne plus afficher ce message", warning_box
            )
            cb.stateChanged.connect(check_changed)

            warning_box.setCheckBox(cb)

            warning_box.show()

    @QtCore.Slot()
    def data_changed(self, topLeft, bottomRight, roles):
        if topLeft.column() > 0 or QtCore.Qt.EditRole not in roles:
            return
        if not self.project.are_videos_ready():
            # TODO connect a signal
            self.pop_warning_box(
                "Les vidéos sont en cours de téléchargement. L'analyse du segment débutera automatiquement."
            )
            return
        try:
            segment = self.segment_model.get_segment_from_index(topLeft)
        except Exception as e:
            self.pop_error_box(str(e))
            return
        if not segment.need_analysis():
            return
        if self.previewer is not None:
            self.previewer.stop()
        preview.previewManager.cancel(segment)

        def compute_finish():
            filter(lambda x: x.segment != segment, self.analyze_worker_list)

        def compute_success(_):
            preview.previewManager.compute_previews(
                self.threadpool, segment.combos[:10]
            )

        def compute_error(err):
            self.pop_error_box(err)

        compute_worker = AnalyzeWorker(segment)
        self.analyze_worker_list.append(compute_worker)

        compute_worker.signals.finished.connect(compute_finish)
        compute_worker.signals.result.connect(compute_success)
        compute_worker.signals.error.connect(compute_error)
        compute_worker.stateChanged.connect(
            self.segment_model.analysis_state_changed
        )
        self.threadpool.start(compute_worker)

    def cancel_compute(self):
        segment = self.get_selected_segment()

        # Interrupts all analyzing threads corresponding to current segment
        list(
            map(
                lambda x: x.interrupt(),
                filter(
                    lambda x: x.segment == segment, self.analyze_worker_list
                ),
            )
        )

    def get_selected_i(self):
        if len(self.listView.selectionModel().selectedIndexes()) > 0:
            return self.listView.selectionModel().selectedIndexes()[0].row()
        return -1

    def get_selected_index(self):
        return self.listView.selectionModel().selectedIndexes()[0]

    def get_selected_segment(self):
        return self.segment_model.get_segment_from_index(
            self.get_selected_index()
        )

    @QtCore.Slot()
    def _preview_combo(self, previewer):
        current_combo = self.segment_model.get_chosen_from_index(
            self.get_selected_index()
        ).get_chosen_combo()
        if previewer is not None and (
            previewer.combo is None or current_combo == previewer.combo
        ):
            if self.previewer is not None:
                self.previewer.stop()
            self.previewer = previewer
            self.previewer.run(self.pixmap, self.graphicsView, True)

    def preview_combo(self, i):
        self.mapper.submit()
        if self.previewer is not None:
            self.previewer.stop()
        segment = self.get_selected_segment()
        preview.previewManager.compute_previews(
            self.threadpool, segment.combos[i : i + 1], self._preview_combo
        )
        preview.previewManager.compute_previews(
            self.threadpool, segment.combos[i + 1 : i + 6]
        )
        self._preview_combo(preview.blank_preview)

    def closeEvent(self, event):
        if self.wants_to_quit():
            event.accept()
        else:
            event.ignore()

    def new(self):
        findDialog = NewProjectDialog(self)
        seed, urls = findDialog.get_project_settings()
        self.open_project(Project(None, seed, urls))
        self.segment_model.command_stack.resetClean()

    def open(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open p00p project"),
            None,
            self.tr("P00p project (*.p00p);;All Files (*)"),
        )
        try:
            self.open_project(load_project(path))
            self.segment_model.command_stack.setClean()
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
            self.segment_model.command_stack.setClean()
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
        if strict and self.segment_model.is_empty():
            raise Exception("No segment found")

        phonems = []
        for ordered_segment in self.segment_model.get_ordered_segments():
            if ordered_segment.get_associated_segment().need_analysis():
                if strict:
                    raise Exception("A segment have not been analyzed")
            else:
                combo = ordered_segment.get_chosen_combo()
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
