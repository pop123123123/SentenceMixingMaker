import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

from data_model.segment import AnalysisState, Segment

GET_PREFIX = "get_"
SET_PREFIX = "set_"
COLUMN_INDEX_TO_ATTRIBUTE = {
    0: "sentence",
    1: "chosen_combo_index",
    2: "analysis_state",
}


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
                segment = self.get_segment_from_index(index)
                if segment.analysis_state == AnalysisState.NEED_ANALYSIS:
                    return QtGui.QIcon.fromTheme("dialog-warning")
                if segment.analysis_state == AnalysisState.ANALYZING:
                    return QtGui.QIcon.fromTheme("view-refresh")

        if role == QtCore.Qt.EditRole:
            return str(data)

        """
        if role == QtCore.Qt.TextColorRole:
            state = self.project.segments[index.row()].analysis_state
            if state == AnalysisState.ANALYZED:
                color = QtGui.QColor.fromRgb(0, 0, 0)
            elif state == AnalysisState.ANALYZING:
                color = QtGui.QColor.fromRgb(125, 125, 0)
            elif state == AnalysisState.NEED_ANALYSIS:
                color = QtGui.QColor.fromRgb(255, 0, 0)
            return color
        """

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            topleft = index.sibling(0, index.row())
            bottomright = index
            self._set_attribute_from_index(index, value)
            self.dataChanged.emit(topleft, bottomright, (QtCore.Qt.EditRole))

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
