# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_NewProject(object):
    def setupUi(self, NewProject):
        if not NewProject.objectName():
            NewProject.setObjectName(u"NewProject")
        NewProject.resize(602, 358)
        self.verticalLayout = QVBoxLayout(NewProject)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(NewProject)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.seed = QLineEdit(NewProject)
        self.seed.setObjectName(u"seed")

        self.horizontalLayout_2.addWidget(self.seed)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.label_2 = QLabel(NewProject)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.url_list = QListWidget(NewProject)
        self.url_list.setObjectName(u"url_list")

        self.verticalLayout.addWidget(self.url_list)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.add_button = QPushButton(NewProject)
        self.add_button.setObjectName(u"add_button")

        self.horizontalLayout.addWidget(self.add_button)

        self.pushButton = QPushButton(NewProject)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(NewProject)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NewProject)
        self.buttonBox.rejected.connect(NewProject.reject)
        self.buttonBox.accepted.connect(NewProject.accept)

        QMetaObject.connectSlotsByName(NewProject)
    # setupUi

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(QCoreApplication.translate("NewProject", u"New project", None))
        self.label.setText(QCoreApplication.translate("NewProject", u"Seed:", None))
        self.label_2.setText(QCoreApplication.translate("NewProject", u"Youtube video URLs:", None))
        self.add_button.setText(QCoreApplication.translate("NewProject", u"Add URL", None))
        self.pushButton.setText(QCoreApplication.translate("NewProject", u"Remove URL", None))
    # retranslateUi

