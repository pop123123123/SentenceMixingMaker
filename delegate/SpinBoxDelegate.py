from PySide2 import QtCore, QtWidgets, QtGui
from model_ui.segment_model import Columns

class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def is_segment_analyzed(self, index):
        """Checks from a given SegmentModel index, if the corresponding
        segment have been analyzed
        """

        analyzed_index = index.siblingAtColumn(Columns.analyzing.value)
        return not index.model().get_attribute_from_index(analyzed_index)

    def createEditor(self, parent, option, index):
        """Returns a new SpinBox widget if the segment have been analyzed"""
        if self.is_segment_analyzed(index):
            return QtWidgets.QSpinBox(parent)
        return None

    def setEditorData(self, editor, index):
        editor.setValue(int(index.data()))

    def editorEvent(self, event, model, option, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        painter.save()

        if not self.is_segment_analyzed(index):
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
            painter.drawRect(option.rect)
            painter.restore()
            return

        option_spinbox = QtWidgets.QStyleOptionSpinBox()
        option_spinbox.rect = option.rect
        option_spinbox.state = option.state

        # By default: white pen (eraser)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))

        # If the segment have been analyzed: we draw information
        # Else, we proint a blank cell
        if self.is_segment_analyzed(index):
            painter.drawText(option_spinbox.rect, QtCore.Qt.AlignCenter,
                             str(index.data()))

            # If the segment associated to the spinbox is selected: green line
            if option_spinbox.state & QtWidgets.QStyle.State_Selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0)))

        # Drawing boundaries
        painter.drawRect(option_spinbox.rect)

        painter.restore()
