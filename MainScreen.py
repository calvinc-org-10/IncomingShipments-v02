# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtCore import (QCoreApplication, QMetaObject, )
from PySide6.QtWidgets import (QWidget, )

from cMenu.kls_cMenu import cMenu
from forms import std_windowsize


class MainScreen(QWidget):
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")
        self.resize(std_windowsize)

        self.theMenu = cMenu(self)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)
    # setupUi

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("MainWindow", u"Incoming Shipments", None))
    # retranslateUi

