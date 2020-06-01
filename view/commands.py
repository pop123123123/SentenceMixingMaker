from PySide2 import QtCore, QtWidgets


class AddSegmentCommand(QtWidgets.QUndoCommand):
    def __init__(
        self, segment_model, list_view, previous_selected_index, new_index
    ):
        QtWidgets.QUndoCommand.__init__(
            self, f"add segment at index {new_index}"
        )
        self.segment_model = segment_model
        self.list_view = list_view
        self.previous_selected_index = previous_selected_index
        self.new_index = new_index

    def undo(self):
        self.segment_model.removeRow(self.new_index)
        index = self.segment_model.createIndex(self.previous_selected_index, 0)
        self.list_view.setCurrentIndex(index)

    def redo(self):
        self.segment_model.insertRow(self.new_index)
        index = self.segment_model.createIndex(self.new_index, 0)
        self.list_view.setCurrentIndex(index)
