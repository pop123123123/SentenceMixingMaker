from PySide2 import QtCore, QtWidgets, QtGui
from model_ui.segment_model import Columns

class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    """This delegates allow a custom display of a spinbox into a tableview"""
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
        """Handles the way editor store new data"""
        editor.setValue(int(index.data()))

    def editorEvent(self, event, model, option, index):
        """This function is used to handle the interactions with handmade
        buttons.
        """

        # If the event is a click event
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # Retrieves the button positions
            left_arrow_button, right_arrow_button = self.get_left_right_arrow_buttons(option)

            # Retrieves the combo index value from the model index
            current_combo_value = int(index.data())

            value_changed = False
            # If left button was clicked, we decrease combo index
            if left_arrow_button.contains(event.pos()):
                if current_combo_value > 0:
                    value_changed = True
                    current_combo_value = current_combo_value - 1

            # If left button was clicked, we increase combo index
            if right_arrow_button.contains(event.pos()):
                # TODO: Globally handle right combo limit (for all the project)
                value_changed = True
                current_combo_value = current_combo_value + 1

            # Report the changes to the model
            if value_changed:
                model.setData(index, current_combo_value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def get_left_arrow_button(self, option):
        """Creates the left arrow button, depending on the option rect area"""
        arrow_buttons_size = option.rect.height()//1.5
        left_arrow_box = QtCore.QRect(
            option.rect.left()+1,
            option.rect.top()+(option.rect.height()//4.5),
            arrow_buttons_size,
            arrow_buttons_size)
        return left_arrow_box

    def paint_left_arrow_button(self, painter, option):
        """Creates the left arrow button et paints it"""
        left_arrow_box = self.get_left_arrow_button(option)
        painter.drawRect(left_arrow_box)
        painter.fillRect(left_arrow_box, QtGui.QColor(255, 255, 255))
        painter.drawText(left_arrow_box, QtCore.Qt.AlignCenter, "<")

    def get_right_arrow_button(self, option):
        """Creates the right arrow button, depending on the option rect area"""
        arrow_buttons_size = option.rect.height()//1.5
        right_arrow_box = QtCore.QRect(
            option.rect.right()-arrow_buttons_size,
            option.rect.top()+(option.rect.height()//4.5),
            arrow_buttons_size,
            arrow_buttons_size)
        return right_arrow_box

    def paint_right_arrow_button(self, painter, option):
        """Creates the right arrow button et paints it"""
        right_arrow_box = self.get_right_arrow_button(option)
        painter.drawRect(right_arrow_box)
        painter.fillRect(right_arrow_box, QtGui.QColor(255, 255, 255))
        painter.drawText(right_arrow_box, QtCore.Qt.AlignCenter, ">")

    def get_left_right_arrow_buttons(self, option):
        return self.get_left_arrow_button(option), self.get_right_arrow_button(option)

    def paint_left_right_arrow_buttons(self, painter, option):
        self.paint_left_arrow_button(painter, option)
        self.paint_right_arrow_button(painter, option)

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
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))

            painter.drawText(option_spinbox.rect, QtCore.Qt.AlignCenter,
                             str(index.data()))

            self.paint_left_right_arrow_buttons(painter, option_spinbox)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))

            # If the segment associated to the spinbox is selected: green line
            if option_spinbox.state & QtWidgets.QStyle.State_Selected:
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0)))

        # Drawing boundaries
        painter.drawRect(option_spinbox.rect)

        painter.restore()

    def sizeHint(self, option, index):
        """Gives an hint about the minimal size of the element to the view"""
        number_of_digits_to_draw = len(str(index.data()))
        arrow_button_width = 25

        width = number_of_digits_to_draw * 10 + 2 * arrow_button_width
        height = 45

        return QtCore.QSize(width, height)
