import json

import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

from data_model.segment import Segment
from worker import AnalysisState

GET_PREFIX = "get_"
SET_PREFIX = "set_"
COLUMN_INDEX_TO_ATTRIBUTE = {
    0: "sentence",
    1: "chosen_combo_index",
    2: "analyzing",
}


class ChosenCombo:
    def __init__(self, project, sentence="", index=0):
        self.project = project
        self.sentence = sentence
        self.index = index

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

    def get_analysis_state(self):
        return self.get_associated_segment(self.project).get_analysis_state()

    def set_analysis_state(self, state):
        return self.get_associated_segment().set_analysis_state(state)

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
        self.ordered_segments = []

    def get_segment_from_index(self, index):
        return self.get_chosen_from_index(index).get_associated_segment()

    def get_chosen_from_index(self, index):
        return self.ordered_segments[index.row()]

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
                if len(self.get_segment_from_index(index).combos) == 0:
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
            self._set_attribute_from_index(index, value)
            self.dataChanged.emit(index, index, [role])
        # Used by drag and drog
        elif role == QtCore.Qt.UserRole:
            self.ordered_segments[index.row()] = value
            topleft = index.sibling(0, index.row())
            bottomright = index.sibling(self.columnCount(index), index.row())
            self.dataChanged.emit(topleft, bottomright, [role])
        else:
            return False
        return True

    def rowCount(self, index):
        return len(self.ordered_segments)

    def columnCount(self, index):
        return len(COLUMN_INDEX_TO_ATTRIBUTE)

    def insertRow(self, position):
        return self.insertRows(position, 1, None)

    def insertRows(self, position, count, parent):
        self.beginInsertRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            self.ordered_segments.insert(position, ChosenCombo(self.project))

        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)

        for _ in range(0, count):
            del self.ordered_segments[row]

        self.endRemoveRows()
        return True

    @QtCore.Slot()
    def analysis_state_changed(self, sentence):
        for i, chosen_segment in enumerate(self.ordered_segments):
            if chosen_segment.sentence == sentence:
                topleft = self.index(i, 2)
                bottomright = self.index(i, 2)
                self.dataChanged.emit(
                    topleft, bottomright, (QtCore.Qt.EditRole)
                )

    def flags(self, index):
        default_flags = super().flags(index)

        if index.isValid():
            return QtCore.Qt.ItemFlag.ItemIsDragEnabled | default_flags
        else:
            return QtCore.Qt.ItemFlag.ItemIsDropEnabled | default_flags

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

        for drag_row, segment in row_segments:
            if row != -1 and row != drag_row:
                self.removeRow(drag_row)

                # Because we are inserting after deletion
                # TODO check if this works with multiple drags
                if drag_row < row:
                    row = row - 1

                self.insertRow(row)
                self.setData(
                    self.index(row, 0, QtCore.QModelIndex()),
                    segment,
                    QtCore.Qt.UserRole,
                )
