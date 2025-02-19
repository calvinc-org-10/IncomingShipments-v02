# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtCore import (QCoreApplication, QMetaObject, )
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea )

from cMenu.cMenu import cMenu
from forms import std_windowsize


class MainScreen(QWidget):
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MainWindow")
            
        # self.resize(std_windowsize)
        # scroll_area = QScrollArea()
        # scroll_area.setWidgetResizable(True)
        
        theMenu = cMenu(parent)
        llayout = QVBoxLayout(self)
        llayout.addWidget(theMenu)
        
        self.setLayout(llayout)
        
        # self.theMenu.loadMenu(5, 5) #FIX cMenu!!
        # scroll_area.setWidget(self.theMenu)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)
    # setupUi

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("MainWindow", u"Incoming Shipments", None))
    # retranslateUi

