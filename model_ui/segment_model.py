import PySide2.QtCore as QtCore

from data_model.segment import Segment

GET_PREFIX = "get_"
SET_PREFIX = "set_"
COLUMN_INDEX_TO_ATTRIBUTE = {0: "sentence", 1: "chosen_combo_index"}


class SegmentModel(QtCore.QAbstractTableModel):
    def __init__(self, project, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)
        self.project = project

    def get_segment_from_index(self, index):
        return self.project.segments[index.row()]

    def get_attribute_from_index(self, index):
        global GET_PREFIX
        global COLUMN_TO_ATTRIBUTE

        segment = self.get_segment_from_index(index)

        getter_name = GET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        getter = getattr(segment, getter_name, None)

        return getter()

    def _set_attribute_from_index(self, index, new_value):
        global SET_PREFIX
        global COLUMN_TO_ATTRIBUTE

        segment = self.get_segment_from_index(index)

        setter_name = SET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        setter = getattr(segment, setter_name, None)

        return setter(new_value)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            data = self.get_attribute_from_index(index)
            if data == "":
                return "<Empty>"
            return data

        if role == QtCore.Qt.DecorationRole:
            return self.project.segments[index.row()].need_analysis

        if role == QtCore.Qt.EditRole:
            return self.get_attribute_from_index(index)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            self._set_attribute_from_index(index, value)
            # self.project.segments[index] = value
            self.dataChanged.emit(index, index, (QtCore.Qt.EditRole,))
        else:
            return False
        return True

    def rowCount(self, index):
        return len(self.project.segments)

    def columnCount(self, index):
        global COLUMN_INDEX_TO_ATTRIBUTE
        return len(COLUMN_INDEX_TO_ATTRIBUTE)

    def insertRow(self, position):
        return self.insertRows(position, 1, None)

    def insertRows(self, position, count, parent):
        self.beginInsertRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            self.project.segments.insert(position, Segment(self.project, ""))

        self.endInsertRows()
        return True

    def removeRow(self, position):
        return self.removeRows(position, 1, None)

    def removeRows(self, position, count, parent):
        self.beginRemoveRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            del self.project.segments[position]

        self.endRemoveRows()
        return True
