from PySide2 import QtCore, QtWidgets, QtGui

class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return QtWidgets.QSpinBox(parent)

    def setEditorData(self, editor, index):
        editor.setValue(int(index.data()))

    def editorEvent(self, event, model, option, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        painter.save()

        option_spinbox = QtWidgets.QStyleOptionSpinBox()
        option_spinbox.rect = option.rect
        option_spinbox.state = option.state

        painter.drawText(option_spinbox.rect, QtCore.Qt.AlignCenter, str(index.data()))

        if option_spinbox.state & QtWidgets.QStyle.State_Selected:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0)))
            painter.drawRect(option_spinbox.rect)
            painter.restore()
            return

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        painter.drawRect(option_spinbox.rect)

        #super().paint(painter, option, index)

        painter.restore()
        return

        painter.setPen(QtGui.QPen(QtGui.QColor.green))
        print(option_spinbox)
        style_option_spinbox_spinbox = QtWidgets.QStyleOptionSpinBox()
        print(style_option_spinbox_spinbox.buttonSymbols)

        rect = QtCore.QRect(100, 200, 11, 16)
        painter.drawRect(rect)
        painter.fillRect(rect, QtGui.QColor(100, 50, 200))

        painter.restore()

        print("c")
    """
    def sizeHint(self, option, index):
        print("d")
        pass
    """
