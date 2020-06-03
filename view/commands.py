from PySide2 import QtCore, QtWidgets

from model_ui.segment_model import Columns


class AddSegmentCommand(QtWidgets.QUndoCommand):
    def __init__(
        self, segment_model, list_view, previous_selected_row, new_row
    ):
        QtWidgets.QUndoCommand.__init__(
            self, f"add segment at index {new_row}"
        )
        self.segment_model = segment_model
        self.list_view = list_view
        self.previous_selected_row = previous_selected_row
        self.new_row = new_row

    def undo(self):
        self.segment_model.removeRow(self.new_row)
        index = self.segment_model.createIndex(self.previous_selected_row, 0)
        self.list_view.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.ClearAndSelect
        )

    def redo(self):
        self.segment_model.insertRow(self.new_row)
        index = self.segment_model.createIndex(self.new_row, 0)
        self.list_view.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.ClearAndSelect
        )


class RemoveSegmentCommand(QtWidgets.QUndoCommand):
    def __init__(self, segment_model, list_view, row):
        QtWidgets.QUndoCommand.__init__(self, f"remove segment {row}")
        self.segment_model = segment_model
        self.list_view = list_view
        self.row = row

        self.sentence = None
        self.combo_index = None

    def undo(self):
        self.segment_model.insertRow(self.row)
        sentence_index = self.segment_model.createIndex(
            self.row, Columns.sentence.value
        )
        combo_index_index = self.segment_model.createIndex(
            self.row, Columns.combo_index.value
        )
        self.segment_model.setData(sentence_index, self.sentence)
        self.segment_model.setData(combo_index_index, self.combo_index)

        self.list_view.selectionModel().setCurrentIndex(
            sentence_index, QtCore.QItemSelectionModel.ClearAndSelect
        )

    def redo(self):
        sentence_index = self.segment_model.createIndex(
            self.row, Columns.sentence.value
        )
        combo_index_index = self.segment_model.createIndex(
            self.row, Columns.combo_index.value
        )
        self.sentence = self.segment_model.data(
            sentence_index, QtCore.Qt.EditRole
        )
        self.combo_index = int(
            self.segment_model.data(combo_index_index, QtCore.Qt.EditRole)
        )

        self.segment_model.removeRow(self.row)
        index = self.segment_model.createIndex(self.row - 1, 0)
        self.list_view.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.ClearAndSelect
        )
