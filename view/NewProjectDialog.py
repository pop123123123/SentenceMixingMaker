# This Python file uses the following encoding: utf-8
from PySide2 import QtCore, QtWidgets

from ui.generated.new import Ui_NewProject


class NewProjectDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_NewProject()
        self.ui.setupUi(self)
        self.ui.add_button.clicked.connect(self.add_url)
        self.ui.remove_button.clicked.connect(self.remove_url)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
            False
        )

    def add_url(self):
        self.ui.url_list.addItem("https://www.youtube.com/watch?v=XmiBSEEYRoo")
        item = self.ui.url_list.item(self.ui.url_list.count() - 1)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
            True
        )
        self.ui.url_list.editItem(item)

    def remove_url(self):
        selected_indexes = self.ui.url_list.selectedIndexes()
        if len(selected_indexes) > 0:
            index = selected_indexes[0]
            self.ui.url_list.takeItem(index.row())

    def get_project_settings(self):
        ret = self.exec_()
        if ret == 1:
            seed = self.ui.seed.text()
            urls = [
                self.ui.url_list.item(i).text()
                for i in range(self.ui.url_list.count())
            ]
            return seed, urls
        return (None, None)
