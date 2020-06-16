import json
from enum import Enum

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets

import view.commands
from data_model.segment import Segment
from worker import AnalysisState

GET_PREFIX = "get_"
SET_PREFIX = "set_"
COLUMN_INDEX_TO_ATTRIBUTE = {
    0: "sentence",
    1: "chosen_combo_index",
    2: "analyzing",
}


class Columns(Enum):
    sentence = 0
    combo_index = 1
    analysing = 2


class ChosenCombo:
    def __init__(self, project, sentence="", index=0):
        self.project = project
        self.sentence = sentence
        self.index = index

    def is_ready(self):
        return (
            not self.get_associated_segment().need_analysis()
            and self.sentence != ""
        )

    def get_chosen_combo(self):
        return self.get_associated_segment().combos[self.index]

    def get_associated_segment(self):
        return self.project.get_segment(self.sentence)

    def get_chosen_combo_index(self):
        return self.index

    def set_chosen_combo_index(self, index):
        self.index = index

    def get_sentence(self):
        return self.sentence

    def set_sentence(self, sentence):
        self.sentence = sentence

    def get_analyzing(self):
        return self.get_associated_segment().is_analyzing()

    def set_analysis_state(self, state):
        assert False, "you should not be calling this"

    def to_JSON_serializable(self):
        return {
            "sentence": self.sentence,
            "index": self.index,
        }

    def from_JSON_serializable(project, json_serializable):
        return ChosenCombo(
            project, json_serializable["sentence"], json_serializable["index"]
        )

    def __repr__(self):
        return f'("{self.sentence}", {self.index})'


class SegmentModel(QtCore.QAbstractTableModel):
    def __init__(self, project, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)
        self.project = project
        self.command_stack = QtWidgets.QUndoStack()

    def get_segment_from_index(self, index):
        return self.get_chosen_from_index(index).get_associated_segment()

    def get_chosen_from_index(self, index):
        return self.project.ordered_segments[index.row()]

    def get_chosen_from_row(self, row):
        return self.project.ordered_segments[row]

    def get_attribute_from_index(self, index):
        getter_name = GET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        getter = getattr(self.get_chosen_from_index(index), getter_name, None)

        return getter()

    def _set_attribute_from_index(self, index, new_value):
        setter_name = SET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        setter = getattr(self.get_chosen_from_index(index), setter_name, None)

        return setter(new_value)

    def _formatted_data(self, index):
        data = self.get_attribute_from_index(index)
        column = index.column()
        if column == 1:
            data = str(data)
        elif column == 2:
            data = str(data)

        return data

    def data(self, index, role):
        data = self.get_attribute_from_index(index)

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0 and data == "":
                data = "<Empty>"
            return str(data)

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                if self.get_segment_from_index(index).is_analyzing():
                    return QtGui.QIcon.fromTheme("view-refresh")

        if role == QtCore.Qt.EditRole:
            return str(data)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if (
            role == QtCore.Qt.EditRole
            or role == QtCore.Qt.DisplayRole
            or role == QtCore.Qt.DecorationRole
        ):

            command = view.commands.EditSegmentCommand(
                self, index, self.get_attribute_from_index(index), value, role
            )
            self.command_stack.push(command)
        else:
            return False
        return True

    def rowCount(self, index):
        return len(self.project.ordered_segments)

    def columnCount(self, index):
        return len(COLUMN_INDEX_TO_ATTRIBUTE)

    def insertRow(self, position):
        return self.insertRows(position, 1, None)

    def insertRows(self, position, count, parent):
        self.beginInsertRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            self.project.ordered_segments.insert(
                position, ChosenCombo(self.project)
            )

        self.endInsertRows()
        return True

    def is_empty(self):
        return len(self.project.ordered_segments) == 0

    def get_ordered_segments(self):
        return self.project.ordered_segments

    def count_same_sentence(self, sentence):
        return len(
            list(
                filter(
                    lambda x: x.get_sentence() == sentence,
                    self.project.ordered_segments,
                )
            )
        )

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)

        for _ in range(0, count):
            del self.project.ordered_segments[row]

        self.endRemoveRows()
        return True

    @QtCore.Slot()
    def analysis_state_changed(self, sentence):
        for i, chosen_segment in enumerate(self.project.ordered_segments):
            if chosen_segment.sentence == sentence:
                topleft = self.index(i, 2)
                bottomright = self.index(i, 2)
                self.dataChanged.emit(
                    topleft, bottomright, (QtCore.Qt.EditRole)
                )

    def flags(self, index):
        default_flags = super().flags(index)

        if index.isValid():
            return (
                QtCore.Qt.ItemFlag.ItemIsEditable
                | QtCore.Qt.ItemFlag.ItemIsDragEnabled
                | default_flags
            )
        else:
            return (
                QtCore.Qt.ItemFlag.ItemIsEditable
                | QtCore.Qt.ItemFlag.ItemIsDropEnabled
                | default_flags
            )

    def supportedDragActions(self):
        return QtCore.Qt.MoveAction

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ["text/json"]

    def mimeData(self, indexes):
        data = [
            (
                index.row(),
                self.get_chosen_from_index(index).to_JSON_serializable(),
            )
            for index in indexes
        ]
        dragData = json.dumps(data)
        mimeData = QtCore.QMimeData()
        mimeData.setData("text/json", QtCore.QByteArray(str.encode(dragData)))
        return mimeData

    def dropMimeData(self, data, action, row, column, parent=None):
        if action == QtCore.Qt.DropAction.MoveAction:
            dropData = json.loads(bytes(data.data("text/json")))
            row_segments = list(
                map(
                    lambda x: (
                        x[0],
                        ChosenCombo.from_JSON_serializable(self.project, x[1]),
                    ),
                    dropData,
                )
            )

            row_segments.sort(key=lambda x: x[0], reverse=True)
            row_segments = [
                (from_, row, combo) for from_, combo in row_segments
            ]

            if row != -1:
                self.command_stack.push(
                    view.commands.DragDropCommand(self, row_segments)
                )
