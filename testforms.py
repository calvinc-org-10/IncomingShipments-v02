from collections import namedtuple
from typing import Dict, List, Tuple, Any

from datetime import datetime

from django.db import models

from PySide6.QtCore import (QCoreApplication,
    Qt, Slot,
    QDate,
    QMetaObject, QObject, QPoint, QRect,
    QStringListModel, QModelIndex
    )
from PySide6.QtGui import (QBrush, QColor, QColorConstants, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QWidget,
    QVBoxLayout, QScrollArea, QFrame, QGridLayout, QHBoxLayout, QFormLayout,
    QListWidget,
    QLabel, QPushButton, QLineEdit, QCompleter, QDateEdit, QTabWidget, QTextEdit, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QInputDialog,
    QSizePolicy, 
    )


from cMenu.utils import cDataList, cQRecordsetView
from incShip.models import HBL, Invoices, ShippingForms, Containers, references
from forms import IncShipAppchoiceWidgets, Invoice_singleForm
from forms import std_windowsize, fontFormTitle
from forms import pleaseWriteMe


import time
class Test01(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"Form-Test01")
        self.setGeometry(QRect(0,0,1280,720))
        
        Unsubmitted_Invoices = [Invoices.SmOffStatusCodes.NOTENT, Invoices.SmOffStatusCodes.DRAFT]
        self.recordSet = Invoices.objects.filter(SmOffStatus__in=Unsubmitted_Invoices)
        
        self.area1 = cQRecordsetView(newwidget_fn=lambda: Invoice_singleForm(), parent=self)
        self.area1.setGeometry(100,100,830,500)
        
        for rec in self.recordSet:
            wdgt = Invoice_singleForm(InvRec=rec)
            self.area1.addWidget(wdgt)
            # print(f'loading record {rec.pk}')
        
        self.test2 = IncShipAppchoiceWidgets.chooseSmOffInvStatus(self)
        self.test2.setGeometry(1000,200,140,50)
        self.test2.activated.connect(self.show01)
        
        self.showtest2 = QLabel(self)
        self.showtest2.setGeometry(1000,300,240,120)
        self.showtest2.setWordWrap(True)
    # setupUi
    
    def show01(self, index):
        cDat = self.test2.currentData()
        itDat = 'n/I'
        tx = f'{index=}, {self.test2.currentText()=}, {cDat=}, {itDat=}'
        self.showtest2.setText(tx)
#class Test01

class Test02(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"Frame")
        self.resize(941, 471)
        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(190, 90, 611, 151))
        font = QFont()
        font.setFamilies([u"A little sunshine"])
        font.setPointSize(36)
        self.label.setFont(font)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)
    # setupUi

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Test Window 2"))
        self.label.setText(self.tr("This is test label 1"))
    # retranslateUi
# class Test02

class Test03():
    def __init__(self):
        # just wanna debug ...
        breakpoint()
        pass
    def setProperty(self, dummy1, dummy2):
        pass

class cQFmFldWidg(QWidget):
    _label:QLabel = None
    _mdlField:str = None

    def __init__(self, 
        widgType:type[QWidget], parent:QWidget = None, 
        lblText:str = '', 
        mdlFld:str = '', fldSetter:Slot = None, 
        ):
        
        super().__init__(parent)
            
    def Label(self) -> QLabel:
        ...
    def setLabel(self, txt:str) -> None:
        ...


##############################################################
##############################################################
##############################################################

