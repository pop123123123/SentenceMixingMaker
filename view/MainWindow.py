# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide2 import QtCore, QtGui, QtMultimedia, QtMultimediaWidgets, QtWidgets
from PySide2.QtWidgets import QHeaderView
from sentence_mixing.video_creator.video import create_video_file

import view.commands as commands
import view.video_assembly as video_assembly
from data_model.project import Project, load_project
from model_ui.segment_model import SegmentModel, Columns
from ui.generated.ui_mainwindow import Ui_Sentence
from view import preview
from view.NewProjectDialog import NewProjectDialog
from worker import AnalyzeWorker, AnalyzeWorkerPool, Worker, WorkerSignals

from sentence_mixing.video_creator.download import dl_video

import sentence_mixing as sm
from worker import Worker


def download_video_and_audio(urls):
    vid_paths = list(map(dl_video, urls))
    videos = sm.sentence_mixer.get_videos(urls)

    for video, path in zip(videos, vid_paths):
        n = len(video._base_path)
        assert path[:n] == video._base_path
        video.extension = path[n + 1 :]

    return videos

class MainWindow(Ui_Sentence, QtWidgets.QMainWindow):
    def __init__(self, project):
        QtWidgets.QMainWindow.__init__(self)
        Ui_Sentence.__init__(self)
        self.setupUi(self)

        self.threadpool = QtCore.QThreadPool()

        self.actionNew.triggered.connect(self.new)
        self.actionOpen.triggered.connect(self.open)
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionSave.triggered.connect(self.save)
        self.actionExport.triggered.connect(self.export_all)
        self.actionExport_selection.triggered.connect(self.export_selection)
        self.actionQuit.triggered.connect(self.quit)
        self.actionPreview_current.triggered.connect(self.preview_current)
        self.actionPreview_all.triggered.connect(self.complete_preview)

        self.actionPrevious_Combo.triggered.connect(self.previous_combo)
        self.actionNext_Combo.triggered.connect(self.next_combo)

        self.actionAdd_segment.triggered.connect(self.add_sentence)
        self.actionAdd_Segment_Above.triggered.connect(self.add_sentence_above)
        self.actionAdd_Segment_Below.triggered.connect(self.add_sentence_below)
        self.actionRemove_Segment_s.triggered.connect(self.remove_sentence)

        self.graphicsView = QtWidgets.QGraphicsView()
        self.video_layout.addWidget(self.graphicsView)
        self.graphicsView.setScene(QtWidgets.QGraphicsScene())
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.graphicsView.scene().addItem(self.pixmap)

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

        import delegate.SpinBoxDelegate as spinbox_delegate
        self.tableView.setItemDelegateForColumn(
            Columns.combo_index.value,
            spinbox_delegate.SpinBoxDelegate(self.tableView))

        self.tableView.setColumnHidden(Columns.analyzing.value, True)

        # self.tableView.indexesMoved.connect(self.table_index_change)
        self.tableView.currentChanged = self.table_index_change
        self.tableView.selectionModel().selectionChanged.connect(self.selection_change)
        self.segment_model.dataChanged.connect(self.data_changed)

        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.pushButton_preview.clicked.connect(self.complete_preview)
        self.pushButton_add_sentence.clicked.connect(self.add_sentence)
        self.pushButton_remove_sentence.clicked.connect(self.remove_sentence)
        self.preview_checkBox.clicked.connect(self.set_loop)

        self.previewer = None
        self.threadpool = QtCore.QThreadPool()

        self.analyze_worker_pool = AnalyzeWorkerPool(
            self.segment_model, self.threadpool
        )

        self.show_warning_message = True

        self.preview_loop = False

    def open_project(self, project):
        self.project = project

        self.video_dl_worker = Worker(download_video_and_audio, project.urls[0])

        def init(videos):
            project.init_project(videos)
            for s in project.segments.values():
                self.segment_text_changed(s)

        self.video_dl_worker.signals.result.connect(init)
        self.video_dl_worker.signals.error.connect(print)

        self.threadpool.start(self.video_dl_worker)

        self.segment_model = SegmentModel(project)
        self.tableView.setModel(self.segment_model)

    @QtCore.Slot()
    def stackCleanChanged(self, is_clean):
        self.setWindowModified(not is_clean)

    def add_sentence_above(self):
        i = self.get_first_selected_i()
        command = commands.AddSegmentCommand(
            self.segment_model, self.tableView, i, i
        )
        self.segment_model.command_stack.push(command)

    def add_sentence_below(self):
        i = self.get_first_selected_i()
        command = commands.AddSegmentCommand(
            self.segment_model, self.tableView, i, i + 1
        )
        self.segment_model.command_stack.push(command)

    def add_sentence(self):
        i = self.get_first_selected_i()
        n = self.segment_model.rowCount(self)
        command = commands.AddSegmentCommand(
            self.segment_model, self.tableView, i, n
        )
        self.segment_model.command_stack.push(command)

    def remove_sentence(self):
        segment = self.get_first_selected_segment()
        try:
            # Only interrupt analysis if the sentence is unique in the list
            if (
                self.segment_model.count_same_sentence(segment.get_sentence())
                == 1
            ):
                self.analyze_worker_pool.interrupt_worker(segment)
        # Analysis is already
        except KeyError:
            pass

        selected_rows = self.get_all_selected_i()

        factory = commands.CommandGroupedFactory(self.segment_model, self.tableView)
        grouped_command = factory.make_grouped_remove_segments(selected_rows)
        self.segment_model.command_stack.push(grouped_command)


    def table_index_change(self, current, _previous):
        if _previous.row() != -1:
            preview.previewManager.cancel(
                self.segment_model.get_segment_from_index(_previous)
            )
        if self.previewer is not None and current.row() != _previous.row():
            self.previewer.stop()

    def selection_change(self, newly_selected, newly_deselected):
        selected_segments = self.get_all_selected_segments()

        if len(selected_segments) == 0:
            self.pushButton_remove_sentence.setDisabled(True)
        else:
            self.pushButton_remove_sentence.setDisabled(False)

    def set_loop(self, state):
        self.preview_loop = state
        self.pause(state)

    def pause(self, state):
        if self.previewer is not None:
            if state:
                self.previewer.unpause()
            else:
                self.previewer.pause()

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
        """ This function is triggered when the SegmentModel is changed"""
        if QtCore.Qt.EditRole not in roles:
            return

        # Retrieving involved segment
        try:
            segment = self.segment_model.get_segment_from_index(topLeft)
        except Exception as e:
            self.pop_error_box(str(e))
            return

        if topLeft.column() == Columns.sentence.value:
            self.segment_text_changed(segment)
        elif topLeft.column() == Columns.combo_index.value:
            # If the segment have been already analyzed
            combo_index = int(topLeft.data())
            if segment.is_analyzed():
                self.preview_combo(combo_index)

    def segment_text_changed(self, segment):
        def compute_finish():
            pass

        def compute_success(_):
            preview.previewManager.compute_previews(
                self.threadpool, segment.combos[:10]
            )

        def compute_error(err):
            self.pop_error_box(err)

        already_created = False
        try:
            self.analyze_worker_pool.add_worker(
                segment, compute_finish, compute_success, compute_error
            )
        except KeyError:
            already_created = True

        # If videos are still downloading
        if not self.project.are_videos_ready():
            self.pop_warning_box(
                "Les vidéos sont en cours de téléchargement. L'analyse du segment débutera automatiquement."
            )

            # Lanches the analysis at the end of the downloading if necessary
            if not already_created:

                def exec_worker():
                    self.analyze_worker_pool.launch_thread(segment)

                self.video_dl_worker.signals.finished.connect(exec_worker)
            return

        if not segment.need_analysis():
            return

        if self.previewer is not None:
            self.previewer.stop()
        preview.previewManager.cancel(segment)

        if not already_created:
            self.analyze_worker_pool.launch_thread(segment)

    def get_all_selected_indexes(self):
        # Warning: returns only one index per row
        # In our model, segment_model have three columns, then, selection model
        # will return three selected items per selected segment_model
        # We only keep one index value for each row
        return [index for index in self.tableView.selectionModel().selectedIndexes() if index.column() == Columns.sentence.value]

    def get_all_selected_i(self):
        return [index.row() for index in self.get_all_selected_indexes()]

    def get_all_selected_segments(self):
        return [self.segment_model.get_segment_from_index(index) for index in self.get_all_selected_indexes()]

    def get_first_selected_index(self):
        indexes = self.get_all_selected_indexes()
        if len(indexes):
            return indexes[0]
        return None

    def get_first_selected_i(self):
        index = self.get_first_selected_index()
        if index is not None:
            return index.row()
        return -1

    def get_first_selected_segment(self):
        index = self.get_first_selected_index()
        if index is not None:
            return self.segment_model.get_segment_from_index(
                index
            )
        return None

    @QtCore.Slot()
    def complete_preview(self):
        phonems = self.collect_combos(strict=False)
        previewer = preview.Previewer(None, audio_phonems=phonems)
        if self.previewer is not None:
            self.previewer.stop()
        self.previewer = previewer
        self.previewer.run(self.pixmap, self.graphicsView)

    @QtCore.Slot()
    def _preview_combo(self, previewer):
        current_combo = self.segment_model.get_chosen_from_index(
            self.get_first_selected_index()
        ).get_chosen_combo()
        if previewer is not None and (
            previewer.combo is None or current_combo == previewer.combo
        ):
            if self.previewer is not None:
                self.previewer.stop()
            # self.preview_checkBox.setChecked(True)
            self.previewer = previewer
            self.previewer.run(self.pixmap, self.graphicsView, self.preview_loop)


    def preview_combo(self, i):
        if self.previewer is not None:
            self.previewer.stop()

        segment = self.get_first_selected_segment()
        if segment is not None:
            preview.previewManager.compute_previews(
                self.threadpool, segment.combos[i : i + 1], self._preview_combo
            )
            preview.previewManager.compute_previews(
                self.threadpool, segment.combos[i + 1 : i + 6]
            )
            self._preview_combo(preview.blank_preview)

    def preview_current(self):
        row = self.get_first_selected_i()
        if row >= 0:
            index = self.segment_model.index(row, 1)
            i = self.segment_model.get_attribute_from_index(index)
            self.preview_combo(i)

    def previous_combo(self):
        row = self.get_first_selected_i()
        if row >= 0:
            index = self.segment_model.index(row, 1)
            i = self.segment_model.get_attribute_from_index(index)
            self.segment_model.setData(index, max(i - 1, 0))

    def next_combo(self):
        row = self.get_first_selected_i()
        if row >= 0:
            index = self.segment_model.index(row, 1)
            i = self.segment_model.get_attribute_from_index(index)
            self.segment_model.setData(index, i + 1)

    def closeEvent(self, event):
        if self.wants_to_quit():
            event.accept()
        else:
            event.ignore()

    def new(self):
        findDialog = NewProjectDialog(self)
        seed, urls = findDialog.get_project_settings()
        if urls is not None:
            self.open_project(Project(None, seed, [urls]))
            self.segment_model.command_stack.resetClean()

    def fromNew():
        findDialog = NewProjectDialog(None)
        seed, urls = findDialog.get_project_settings()
        if urls is not None:
            p = Project(None, seed, [urls])
            return MainWindow(p)
        return None

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

    def collect_combos(self, chosen_list=None, strict=True):
        if chosen_list is None:
            chosen_list = self.segment_model.get_ordered_segments()

        if strict and self.segment_model.is_empty():
            raise Exception("No segment found")

        phonems = []
        for ordered_segment in chosen_list:
            if not ordered_segment.is_ready():
                if strict:
                    raise Exception("A segment have not been analyzed")
            else:
                combo = ordered_segment.get_chosen_combo()
                phonems.extend(combo.get_audio_phonems())

        if len(phonems) == 0:
            raise Exception("No analyzed segments")

        return phonems

    def export_selection(self):
        selected_rows = {
            i.row() for i in self.tableView.selectionModel().selectedIndexes()
        }
        chosen = [
            self.segment_model.get_chosen_from_row(r) for r in selected_rows
        ]
        self.export(chosen)

    def export_all(self):
        self.export()

    def export(self, chosen_list=None):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Export p00p project"),
            None,
            self.tr("mp4 video (*.mp4);;All Files (*)"),
        )

        if path == "":
            self.pop_error_box("Path is empty")
            return

        if Path(path).suffix == "":
            path = path + ".mp4"
        elif Path(path).suffix != ".mp4":
            self.pop_error_box("Exported file must have '.mp4' extension")
            return

        # Retrieves phonems of all segments
        try:
            phonems = self.collect_combos(
                chosen_list=chosen_list, strict=False
            )
        except Exception as e:
            self.pop_error_box(str(e))
            return

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
            preview.previewManager.cancel_all()
            QtWidgets.QApplication.quit()
