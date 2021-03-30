from enum import Enum

from PySide2 import QtCore, QtWidgets

import model_ui.segment_model as segm


class CommandIds(Enum):
    edit = 0


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


class EditSegmentCommand(QtWidgets.QUndoCommand):
    mergeable_columns = {segm.Columns.combo_index.value}

    def __init__(self, segment_model, index, old_value, new_value, role):
        QtWidgets.QUndoCommand.__init__(
            self, f"edit segment at index {index.row()}"
        )
        self.segment_model = segment_model
        self.index = index
        self.old_value = old_value
        self.new_value = new_value
        self.role = role

    def undo(self):
        self.segment_model._set_attribute_from_index(
            self.index, self.old_value
        )
        self.segment_model.dataChanged.emit(
            self.index, self.index, [self.role]
        )

    def redo(self):
        self.segment_model._set_attribute_from_index(
            self.index, self.new_value
        )
        self.segment_model.dataChanged.emit(
            self.index, self.index, [self.role]
        )

    def id(self):
        return CommandIds.edit.value

    def mergeWith(self, other):
        if (
            other.id() != self.id()
            or self.index.column() not in self.mergeable_columns
            or self.role != other.role
            or self.index != other.index
        ):
            return False
        self.new_value = other.new_value
        return True


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
            self.row, segm.Columns.sentence.value
        )
        combo_index_index = self.segment_model.createIndex(
            self.row, segm.Columns.combo_index.value
        )

        self.segment_model._set_attribute_from_index(
            sentence_index, self.sentence
        )

        self.segment_model._set_attribute_from_index(
            sentence_index, self.sentence
        )

        self.list_view.selectionModel().setCurrentIndex(
            sentence_index, QtCore.QItemSelectionModel.ClearAndSelect
        )

    def redo(self):
        sentence_index = self.segment_model.createIndex(
            self.row, segm.Columns.sentence.value
        )
        combo_index_index = self.segment_model.createIndex(
            self.row, segm.Columns.combo_index.value
        )
        self.sentence = self.segment_model.data(
            sentence_index, QtCore.Qt.EditRole
        )
        self.combo_index = int(
            self.segment_model.data(combo_index_index, QtCore.Qt.EditRole)
        )

        index = self.segment_model.createIndex(self.row - 1, 0)
        self.list_view.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.ClearAndSelect
        )
        # Remove the row AFTER changing the index, to prevent inconsistencies
        self.segment_model.removeRow(self.row)


class DragDropCommand(QtWidgets.QUndoCommand):
    def __init__(self, segment_model, row_segments):
        QtWidgets.QUndoCommand.__init__(
            self,
            f"drag segment "
            + ", ".join(
                f"{from_} to {to_}" for from_, to_, combo in row_segments
            ),
        )
        self.segment_model = segment_model
        self.row_segments = row_segments

        self.actions = [
            x
            for from_, to_, combo in row_segments
            for x in [[False, from_, combo], [True, to_, combo]]
        ]
        for i in range(len(self.actions)):
            insert, row, _ = self.actions[i]
            for j in range(i, len(self.actions)):
                if self.actions[j][1] > row:
                    self.actions[j][1] += 1 if insert else -1

    def execute(self, invert):
        itera = reversed(self.actions) if invert else self.actions
        for insert, row, combo in itera:
            if insert ^ invert:
                self.segment_model.insertRow(row)
                self.segment_model.setData(
                    self.segment_model.index(row, segm.Columns.sentence.value),
                    combo.sentence,
                    QtCore.Qt.EditRole,
                )
                self.segment_model.setData(
                    self.segment_model.index(
                        row, segm.Columns.combo_index.value
                    ),
                    combo.index,
                    QtCore.Qt.EditRole,
                )
            else:
                self.segment_model.removeRow(row)

    def undo(self):
        self.execute(True)

    def redo(self):
        self.execute(False)
