# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
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
        self.actionUndo = QAction(Sentence)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionUndo.setEnabled(False)
        self.actionRedo = QAction(Sentence)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionRedo.setEnabled(False)
        self.actionCopy = QAction(Sentence)
        self.actionCopy.setObjectName(u"actionCopy")
        self.actionPaste = QAction(Sentence)
        self.actionPaste.setObjectName(u"actionPaste")
        self.actionExport_selection = QAction(Sentence)
        self.actionExport_selection.setObjectName(u"actionExport_selection")
        self.actionPreview_current = QAction(Sentence)
        self.actionPreview_current.setObjectName(u"actionPreview_current")
        self.actionPreview_all = QAction(Sentence)
        self.actionPreview_all.setObjectName(u"actionPreview_all")
        self.actionNext_Combo = QAction(Sentence)
        self.actionNext_Combo.setObjectName(u"actionNext_Combo")
        self.actionPrevious_Combo = QAction(Sentence)
        self.actionPrevious_Combo.setObjectName(u"actionPrevious_Combo")
        self.actionAdd_segment = QAction(Sentence)
        self.actionAdd_segment.setObjectName(u"actionAdd_segment")
        self.actionAdd_Segment_Below = QAction(Sentence)
        self.actionAdd_Segment_Below.setObjectName(u"actionAdd_Segment_Below")
        self.actionAdd_Segment_Above = QAction(Sentence)
        self.actionAdd_Segment_Above.setObjectName(u"actionAdd_Segment_Above")
        self.actionRemove_Segment_s = QAction(Sentence)
        self.actionRemove_Segment_s.setObjectName(u"actionRemove_Segment_s")
        self.centralwidget = QWidget(Sentence)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout.addItem(self.horizontalSpacer_4)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setContextMenuPolicy(Qt.NoContextMenu)
        self.tableView.setAcceptDrops(True)
        self.tableView.setProperty("showDropIndicator", True)
        self.tableView.setDragEnabled(False)
        self.tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.tableView.setDefaultDropAction(Qt.MoveAction)
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setGridStyle(Qt.NoPen)
        self.tableView.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tableView)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_add_sentence = QPushButton(self.centralwidget)
        self.pushButton_add_sentence.setObjectName(u"pushButton_add_sentence")

        self.horizontalLayout_2.addWidget(self.pushButton_add_sentence)

        self.pushButton_remove_sentence = QPushButton(self.centralwidget)
        self.pushButton_remove_sentence.setObjectName(u"pushButton_remove_sentence")
        self.pushButton_remove_sentence.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.pushButton_remove_sentence)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_preview = QPushButton(self.centralwidget)
        self.pushButton_preview.setObjectName(u"pushButton_preview")

        self.horizontalLayout_2.addWidget(self.pushButton_preview)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.video_layout = QVBoxLayout()
        self.video_layout.setObjectName(u"video_layout")
        self.video_layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.verticalLayout_2.addLayout(self.video_layout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.preview_checkBox = QCheckBox(self.centralwidget)
        self.preview_checkBox.setObjectName(u"preview_checkBox")

        self.horizontalLayout_3.addWidget(self.preview_checkBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        Sentence.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Sentence)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 23))
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menucoucou = QMenu(self.menubar)
        self.menucoucou.setObjectName(u"menucoucou")
        self.menuPreview = QMenu(self.menubar)
        self.menuPreview.setObjectName(u"menuPreview")
        Sentence.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Sentence)
        self.statusbar.setObjectName(u"statusbar")
        Sentence.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.tableView, self.pushButton_add_sentence)
        QWidget.setTabOrder(self.pushButton_add_sentence, self.pushButton_preview)

        self.menubar.addAction(self.menucoucou.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuPreview.menuAction())
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPrevious_Combo)
        self.menuEdit.addAction(self.actionNext_Combo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_segment)
        self.menuEdit.addAction(self.actionAdd_Segment_Below)
        self.menuEdit.addAction(self.actionAdd_Segment_Above)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRemove_Segment_s)
        self.menucoucou.addAction(self.actionNew)
        self.menucoucou.addAction(self.actionOpen)
        self.menucoucou.addAction(self.actionSave)
        self.menucoucou.addAction(self.actionSave_as)
        self.menucoucou.addSeparator()
        self.menucoucou.addAction(self.actionExport)
        self.menucoucou.addAction(self.actionExport_selection)
        self.menucoucou.addSeparator()
        self.menucoucou.addAction(self.actionQuit)
        self.menuPreview.addAction(self.actionPreview_current)
        self.menuPreview.addAction(self.actionPreview_all)

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
        self.actionUndo.setText(QCoreApplication.translate("Sentence", u"&Undo", None))
#if QT_CONFIG(shortcut)
        self.actionUndo.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionRedo.setText(QCoreApplication.translate("Sentence", u"&Redo", None))
#if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Y", None))
#endif // QT_CONFIG(shortcut)
        self.actionCopy.setText(QCoreApplication.translate("Sentence", u"&Copy", None))
#if QT_CONFIG(shortcut)
        self.actionCopy.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionPaste.setText(QCoreApplication.translate("Sentence", u"&Paste", None))
#if QT_CONFIG(shortcut)
        self.actionPaste.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionExport_selection.setText(QCoreApplication.translate("Sentence", u"E&xport selection", None))
#if QT_CONFIG(shortcut)
        self.actionExport_selection.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Shift+E", None))
#endif // QT_CONFIG(shortcut)
        self.actionPreview_current.setText(QCoreApplication.translate("Sentence", u"Preview current", None))
#if QT_CONFIG(shortcut)
        self.actionPreview_current.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Space", None))
#endif // QT_CONFIG(shortcut)
        self.actionPreview_all.setText(QCoreApplication.translate("Sentence", u"Preview all", None))
#if QT_CONFIG(shortcut)
        self.actionPreview_all.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Return", None))
#endif // QT_CONFIG(shortcut)
        self.actionNext_Combo.setText(QCoreApplication.translate("Sentence", u"Next Combo", None))
#if QT_CONFIG(shortcut)
        self.actionNext_Combo.setShortcut(QCoreApplication.translate("Sentence", u"Right", None))
#endif // QT_CONFIG(shortcut)
        self.actionPrevious_Combo.setText(QCoreApplication.translate("Sentence", u"Previous Combo", None))
#if QT_CONFIG(shortcut)
        self.actionPrevious_Combo.setShortcut(QCoreApplication.translate("Sentence", u"Left", None))
#endif // QT_CONFIG(shortcut)
        self.actionAdd_segment.setText(QCoreApplication.translate("Sentence", u"Add Segment", None))
        self.actionAdd_Segment_Below.setText(QCoreApplication.translate("Sentence", u"Add Segment Below", None))
#if QT_CONFIG(shortcut)
        self.actionAdd_Segment_Below.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Down", None))
#endif // QT_CONFIG(shortcut)
        self.actionAdd_Segment_Above.setText(QCoreApplication.translate("Sentence", u"Add Segment Above", None))
#if QT_CONFIG(shortcut)
        self.actionAdd_Segment_Above.setShortcut(QCoreApplication.translate("Sentence", u"Ctrl+Up", None))
#endif // QT_CONFIG(shortcut)
        self.actionRemove_Segment_s.setText(QCoreApplication.translate("Sentence", u"Remove Segment(s)", None))
#if QT_CONFIG(shortcut)
        self.actionRemove_Segment_s.setShortcut(QCoreApplication.translate("Sentence", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.label.setText(QCoreApplication.translate("Sentence", u"Sentences", None))
        self.pushButton_add_sentence.setText(QCoreApplication.translate("Sentence", u"Add", None))
        self.pushButton_remove_sentence.setText(QCoreApplication.translate("Sentence", u"Remove", None))
        self.pushButton_preview.setText(QCoreApplication.translate("Sentence", u"Preview", None))
        self.preview_checkBox.setText(QCoreApplication.translate("Sentence", u"Play", None))
        self.menuEdit.setTitle(QCoreApplication.translate("Sentence", u"&Edit", None))
        self.menucoucou.setTitle(QCoreApplication.translate("Sentence", u"Fi&le", None))
        self.menuPreview.setTitle(QCoreApplication.translate("Sentence", u"Preview", None))
    # retranslateUi

