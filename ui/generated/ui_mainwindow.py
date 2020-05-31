# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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


class Ui_Sentence(object):
    def setupUi(self, Sentence):
        if not Sentence.objectName():
            Sentence.setObjectName(u"Sentence")
        Sentence.resize(800, 600)
        self.actionNew = QAction(Sentence)
        self.actionNew.setObjectName(u"actionNew")
        self.actionOpen = QAction(Sentence)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(Sentence)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(Sentence)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionExport = QAction(Sentence)
        self.actionExport.setObjectName(u"actionExport")
        self.actionQuit = QAction(Sentence)
        self.actionQuit.setObjectName(u"actionQuit")
        self.centralwidget = QWidget(Sentence)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.listView = QListView(self.centralwidget)
        self.listView.setObjectName(u"listView")

        self.verticalLayout.addWidget(self.listView)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_add_sentence = QPushButton(self.centralwidget)
        self.pushButton_add_sentence.setObjectName(u"pushButton_add_sentence")

        self.horizontalLayout_2.addWidget(self.pushButton_add_sentence)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_2.addWidget(self.pushButton_3)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_sentence = QLineEdit(self.centralwidget)
        self.lineEdit_sentence.setObjectName(u"lineEdit_sentence")

        self.horizontalLayout.addWidget(self.lineEdit_sentence)

        self.pushButton_sentence_edit = QPushButton(self.centralwidget)
        self.pushButton_sentence_edit.setObjectName(u"pushButton_sentence_edit")

        self.horizontalLayout.addWidget(self.pushButton_sentence_edit)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.video_layout = QVBoxLayout()
        self.video_layout.setObjectName(u"video_layout")
        self.video_layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.verticalLayout_2.addLayout(self.video_layout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.spinBox_index = QSpinBox(self.centralwidget)
        self.spinBox_index.setObjectName(u"spinBox_index")

        self.horizontalLayout_3.addWidget(self.spinBox_index)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.pushButton_compute = QPushButton(self.centralwidget)
        self.pushButton_compute.setObjectName(u"pushButton_compute")
        self.pushButton_compute.setEnabled(False)

        self.verticalLayout_2.addWidget(self.pushButton_compute)

        self.pushButton_cancel_compute = QPushButton(self.centralwidget)
        self.pushButton_cancel_compute.setObjectName(u"pushButton_cancel_compute")
        self.pushButton_cancel_compute.setEnabled(False)

        self.verticalLayout_2.addWidget(self.pushButton_cancel_compute)

        Sentence.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Sentence)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 32))
        self.menucoucou = QMenu(self.menubar)
        self.menucoucou.setObjectName(u"menucoucou")
        Sentence.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Sentence)
        self.statusbar.setObjectName(u"statusbar")
        Sentence.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.listView, self.pushButton_add_sentence)
        QWidget.setTabOrder(self.pushButton_add_sentence, self.pushButton_3)
        QWidget.setTabOrder(self.pushButton_3, self.lineEdit_sentence)
        QWidget.setTabOrder(self.lineEdit_sentence, self.pushButton_sentence_edit)
        QWidget.setTabOrder(self.pushButton_sentence_edit, self.pushButton_compute)

        self.menubar.addAction(self.menucoucou.menuAction())
        self.menucoucou.addAction(self.actionNew)
        self.menucoucou.addAction(self.actionOpen)
        self.menucoucou.addAction(self.actionSave)
        self.menucoucou.addAction(self.actionSave_as)
        self.menucoucou.addSeparator()
        self.menucoucou.addAction(self.actionExport)
        self.menucoucou.addSeparator()
        self.menucoucou.addAction(self.actionQuit)

        self.retranslateUi(Sentence)

        QMetaObject.connectSlotsByName(Sentence)
    # setupUi

    def retranslateUi(self, Sentence):
        Sentence.setWindowTitle(QCoreApplication.translate("Sentence", u"Sentence Mixing Maker[*]", None))
        self.actionNew.setText(QCoreApplication.translate("Sentence", u"&New...", None))
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("Sentence", u"&Open...", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("Sentence", u"&Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_as.setText(QCoreApplication.translate("Sentence", u"Sa&ve as...", None))
#if QT_CONFIG(shortcut)
        self.actionSave_as.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionExport.setText(QCoreApplication.translate("Sentence", u"&Export...", None))
#if QT_CONFIG(shortcut)
        self.actionExport.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+E", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("Sentence", u"&Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.label.setText(QCoreApplication.translate("Sentence", u"Sentences", None))
        self.pushButton_add_sentence.setText(QCoreApplication.translate("Sentence", u"Add", None))
        self.pushButton_3.setText(QCoreApplication.translate("Sentence", u"Preview", None))
        self.pushButton_sentence_edit.setText(QCoreApplication.translate("Sentence", u"Submit", None))
        self.pushButton_compute.setText(QCoreApplication.translate("Sentence", u"Compute", None))
        self.pushButton_cancel_compute.setText(QCoreApplication.translate("Sentence", u"Cancel computing", None))
        self.menucoucou.setTitle(QCoreApplication.translate("Sentence", u"Fi&le", None))
    # retranslateUi

