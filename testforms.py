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


class refsForm(QWidget):
    _linkedModelRefs:Dict[references.refTblChoices, Tuple[models.Model, str]] = {
        references.refTblChoices.Invoices      : (Invoices, 'Invoice'), 
        references.refTblChoices.ShippingForms : (ShippingForms, 'ShippingForm'), 
        references.refTblChoices.HBL           : (HBL, 'HBL'), 
        references.refTblChoices.Containers    : (Containers, 'Container'), 
    }

    currRec:references = None
    formFields:Dict[str, Tuple[QWidget, Any]] = {}
    linkedRecs:Dict[references.refTblChoices, Any] = { tbl: None for tbl in _linkedModelRefs}
    linkedFldNames:Dict[references.refTblChoices, str] = {key:val[1] for key, val in _linkedModelRefs.items()}
    
    # grid positions in Detail part of form
    lnkTblcolumnNum:Dict[references.refTblChoices, int] = {
        references.refTblChoices.HBL           : 0,
        references.refTblChoices.ShippingForms : 1,
        references.refTblChoices.Containers    : 2,
        references.refTblChoices.Invoices      : 3,
    }
    rowLabel, rowData = (0, 1)

    def __init__(self, parent:QWidget = None):
        super().__init__(parent)

        if not self.objectName():
            self.setObjectName(u"Form")
        # self.resize(std_windowsize)
        # self.resize(std_windowsize.width(), std_windowsize.height()) # this is a temporary fix
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        ### FormHdr

        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = QLabel()
        wdgt = self.lblFormName
        wdgt.setObjectName(u"lblFormName")
        wdgt.setFont(fontFormTitle)
        wdgt.setFrameShape(QFrame.Shape.Panel)
        wdgt.setFrameShadow(QFrame.Shadow.Raised)
        wdgt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wdgt.setWordWrap(True)
        self.layoutFormHdr.addWidget(wdgt)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addSpacing(10)

        ### FormMainTop

        self.layoutFormMainTop = QHBoxLayout()
        self.layoutFormMainTopLeft = QFormLayout()
        self.layoutFormMainTopRight = QVBoxLayout()
        self.layoutFormMainTop.addLayout(self.layoutFormMainTopLeft)
        self.layoutFormMainTop.addLayout(self.layoutFormMainTopRight)
        
        self.lblRecID = QLabel()
        self.lblRecID.setProperty('field', 'id')
        self.formFields['id'] = (self.lblRecID, None)
        refid_codeblock = True      # I do this to emphasize a logical codeblock unit
        if refid_codeblock:
            self.lyout_refidBlock = QHBoxLayout()
            refdict = {rec.pk: rec.refName for rec in references.objects.all()}
            self.dlistrefid = cDataList(refdict)
            self.dlistrefid.setProperty('field', 'refName')
            self.formFields['refName'] = (self.dlistrefid, None)
            self.dlistrefid.editingFinished.connect(self.getRecordFromGoto)
            self.lblrefidExpln = QLabel(self)
            self.lblrefidExpln.setText(self.tr('(if the ref id you enter doesn\'t exist, it will be created)'))
            self.lblrefidExpln.setWordWrap(True)
            self.lyout_refidBlock.addWidget(self.dlistrefid)
            self.lyout_refidBlock.addWidget(self.lblrefidExpln)
        FilePath_codeblock = True      # I do this to emphasize a logical codeblock unit
        if FilePath_codeblock:
            self.lyout_FilePathBlock = QHBoxLayout()
            self.lnedtFilePath = QLineEdit(self)
            self.lnedtFilePath.setProperty('field', 'FilePath')
            self.formFields['FilePath'] = (self.lnedtFilePath, None)
            self.lnedtFilePath.editingFinished.connect(lambda: self.changeField(self.lnedtFilePath))
            self.btnChooseFilePaths = QPushButton(self.tr('Choose Files'),self)
            self.btnChooseFilePaths.clicked.connect(lambda: self.ChooseFiles())
            self.lyout_FilePathBlock.addWidget(self.lnedtFilePath)
            self.lyout_FilePathBlock.addWidget(self.btnChooseFilePaths)
        self.txtedtNotes = QTextEdit(); 
        self.txtedtNotes.setProperty('field', 'notes')
        self.formFields['notes'] = (self.txtedtNotes, None)
        self.txtedtNotes.textChanged.connect(lambda: self.changeField(self.txtedtNotes))

        self.layoutFormMainTopLeft.addRow('reference id', self.lyout_refidBlock)
        self.layoutFormMainTopLeft.addRow('File Refs', self.lyout_FilePathBlock)
        self.layoutFormMainTopLeft.addRow(self.tr('notes'), self.txtedtNotes)

        self.layoutFormMainTopRight.addWidget(self.lblRecID)
        self.layoutFormMainTopRight.addSpacing(10)
        self.btnCommit = QPushButton()
        self.btnCommit.clicked.connect(lambda: self.writeRecord())
        self.layoutFormMainTopRight.addWidget(self.btnCommit)

        self.layoutForm.addLayout(self.layoutFormMainTop)
        self.layoutForm.addSpacing(10)

        ### FormMainDetail

        self.layoutFormMainDetail = QGridLayout()
        
        columnHBL = self.lnkTblcolumnNum[references.refTblChoices.HBL]
        columnContainers = self.lnkTblcolumnNum[references.refTblChoices.Containers]
        columnShipForms = self.lnkTblcolumnNum[references.refTblChoices.ShippingForms]
        columnInvoices = self.lnkTblcolumnNum[references.refTblChoices.Invoices]
        rowLabel, rowData \
            = self.rowLabel, self.rowData
        #
        self.wdgtDetail = [[None for row in (rowLabel, rowData)] for col in (columnHBL, columnContainers, columnShipForms, columnInvoices)]
        #
        self.wdgtDetail[columnHBL][rowLabel] = QLabel('HBL', self)
        self.wdgtDetail[columnHBL][rowLabel].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wdgtDetail[columnContainers][rowLabel] = QLabel(self.tr('Container'), self)
        self.wdgtDetail[columnContainers][rowLabel].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wdgtDetail[columnShipForms][rowLabel] = QLabel(self.tr('Shipping Form'), self)
        self.wdgtDetail[columnShipForms][rowLabel].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wdgtDetail[columnInvoices][rowLabel] = QLabel(self.tr('Invoice'), self)
        self.wdgtDetail[columnInvoices][rowLabel].setAlignment(Qt.AlignmentFlag.AlignCenter)
        #
        self.wdgtDetail[columnHBL][rowData] = IncShipAppchoiceWidgets.chooseHBL(parent=self)
        self.wdgtDetail[columnHBL][rowData].setProperty('field', 'HBL')
        self.formFields['HBL'] = (self.wdgtDetail[columnHBL][rowData], None)
        self.wdgtDetail[columnHBL][rowData].editingFinished.connect(lambda: self.changeField(self.wdgtDetail[columnHBL][rowData]))
        self.wdgtDetail[columnInvoices][rowData] = IncShipAppchoiceWidgets.chooseInvoice(parent=self)
        self.wdgtDetail[columnInvoices][rowData].setProperty('field', 'Invoice')
        self.formFields['Invoice'] = (self.wdgtDetail[columnInvoices][rowData], None)
        self.wdgtDetail[columnInvoices][rowData].editingFinished.connect(lambda: self.changeField(self.wdgtDetail[columnInvoices][rowData]))
        self.wdgtDetail[columnContainers][rowData] = IncShipAppchoiceWidgets.chooseContainer(parent=self)
        self.wdgtDetail[columnContainers][rowData].setProperty('field', 'Container')
        self.formFields['Container'] = (self.wdgtDetail[columnContainers][rowData], None)
        self.wdgtDetail[columnContainers][rowData].editingFinished.connect(lambda: self.changeField(self.wdgtDetail[columnContainers][rowData]))
        self.wdgtDetail[columnShipForms][rowData] = IncShipAppchoiceWidgets.chooseShipForm(parent=self)
        self.wdgtDetail[columnShipForms][rowData].setProperty('field', 'ShippingForm')
        self.formFields['ShippingForm'] = (self.wdgtDetail[columnShipForms][rowData], None)
        self.wdgtDetail[columnShipForms][rowData].editingFinished.connect(lambda: self.changeField(self.wdgtDetail[columnShipForms][rowData]))
        # TODO: HOT! connect procs for new entries
        # TODO: HOT! set for dirty on change

        for row in (rowLabel, rowData):
            for col in (columnHBL, columnContainers, columnShipForms, columnInvoices):
                self.layoutFormMainDetail.addWidget(self.wdgtDetail[col][row],row,col)
        
        newDetailrow = self.layoutFormMainDetail.rowCount()
        Company_codeblock = True      # I do this to emphasize a logical codeblock unit
        if Company_codeblock:
            self.layoutBlockCompany = QHBoxLayout()
            self.lblCompany = QLabel()
            self.comboCompany = IncShipAppchoiceWidgets.chooseCompany()
            self.comboCompany.setProperty('field', 'Company')
            self.formFields['Company'] = (self.comboCompany, 'HBL')
            self.comboCompany.activated.connect(lambda: self.changeField(self.comboCompany))
            self.layoutBlockCompany.addWidget(self.lblCompany)
            self.layoutBlockCompany.addWidget(self.comboCompany)
        Mode_codeblock = True      # I do this to emphasize a logical codeblock unit
        if Mode_codeblock:
            self.layoutBlockMode = QHBoxLayout()
            self.lblMode = QLabel()
            self.comboMode = IncShipAppchoiceWidgets.chooseFreightType()
            self.comboMode.setProperty('field', 'FreightType')
            self.formFields['FreightType'] = (self.comboMode, 'HBL')
            self.comboMode.activated.connect(lambda: self.changeField(self.comboMode))
            self.layoutBlockMode.addWidget(self.lblMode)
            self.layoutBlockMode.addWidget(self.comboMode)
        Origin_codeblock = True      # I do this to emphasize a logical codeblock unit
        if Origin_codeblock:
            self.layoutBlockOrigin = QHBoxLayout()
            self.lblOrigin = QLabel()
            self.comboOrigin = IncShipAppchoiceWidgets.chooseOrigin()
            self.comboOrigin.setProperty('field', 'Origin')
            self.formFields['Origin'] = (self.comboOrigin, 'HBL')
            self.comboOrigin.activated.connect(lambda: self.changeField(self.comboOrigin))
            self.layoutBlockOrigin.addWidget(self.lblOrigin)
            self.layoutBlockOrigin.addWidget(self.comboOrigin)
        self.layoutFormMainDetail.addLayout(self.layoutBlockCompany,newDetailrow,0)
        self.layoutFormMainDetail.addLayout(self.layoutBlockMode,newDetailrow,1)
        self.layoutFormMainDetail.addLayout(self.layoutBlockOrigin,newDetailrow,2)
        
        newDetailrow += 1
        self.lblDateHdr = QLabel()
        font1 = QFont()
        font1.setFamilies(["Arial Black"])
        font1.setUnderline(True)
        self.lblDateHdr.setFont(font1)
        self.layoutFormMainDetail.addWidget(self.lblDateHdr,newDetailrow,0)
        
        newDetailrow += 1
        
        PickupDt_codeblock = True      # I do this to emphasize a logical codeblock unit
        if PickupDt_codeblock:
            self.layoutBlockPickupDt = QHBoxLayout()
            self.lblPickupDt = QLabel()
            self.dtedPickupDt = QDateEdit()
            self.dtedPickupDt.setProperty('field', 'PickupDt')
            self.formFields['PickupDt'] = (self.dtedPickupDt, 'HBL')
            self.dtedPickupDt.userDateChanged.connect(lambda dt: self.changeField(self.dtedPickupDt))
            self.layoutBlockPickupDt.addWidget(self.lblPickupDt)
            self.layoutBlockPickupDt.addWidget(self.dtedPickupDt)
        ETA_codeblock = True      # I do this to emphasize a logical codeblock unit
        if ETA_codeblock:
            self.layoutBlockETA = QHBoxLayout()
            self.lblETA = QLabel()
            self.dtedETA = QDateEdit()
            self.dtedETA.setProperty('field', 'ETA')
            self.formFields['ETA'] = (self.dtedETA, 'HBL')
            self.dtedETA.userDateChanged.connect(lambda dt: self.changeField(self.dtedETA))
            self.layoutBlockETA.addWidget(self.lblETA)
            self.layoutBlockETA.addWidget(self.dtedETA)
        DelivAppt_codeblock = True      # I do this to emphasize a logical codeblock unit
        if DelivAppt_codeblock:
            self.layoutBlockDelivAppt = QHBoxLayout()
            self.lblDelivAppt = QLabel()
            self.dtedDelivAppt = QDateEdit()
            self.dtedDelivAppt.setProperty('field', 'DelivAppt')
            self.formFields['DelivAppt'] = (self.dtedDelivAppt, 'Container')
            self.dtedDelivAppt.userDateChanged.connect(lambda dt: self.changeField(self.dtedDelivAppt))
            self.layoutBlockDelivAppt.addWidget(self.lblDelivAppt)
            self.layoutBlockDelivAppt.addWidget(self.dtedDelivAppt)
        LFD_codeblock = True      # I do this to emphasize a logical codeblock unit
        if LFD_codeblock:
            self.layoutBlockLFD = QHBoxLayout()
            self.lblLFD = QLabel()
            self.dtedLFD = QDateEdit()
            self.dtedLFD.setProperty('field', 'LFD')
            self.formFields['LFD'] = (self.dtedLFD, 'Container')
            self.dtedLFD.userDateChanged.connect(lambda dt: self.changeField(self.dtedLFD))
            self.layoutBlockLFD.addWidget(self.lblLFD)
            self.layoutBlockLFD.addWidget(self.dtedLFD)
        self.layoutFormMainDetail.addLayout(self.layoutBlockPickupDt,newDetailrow,0)
        self.layoutFormMainDetail.addLayout(self.layoutBlockETA,newDetailrow,1)
        self.layoutFormMainDetail.addLayout(self.layoutBlockDelivAppt,newDetailrow,2)
        self.layoutFormMainDetail.addLayout(self.layoutBlockLFD,newDetailrow,3)
        
        self.layoutForm.addLayout(self.layoutFormMainDetail)

        # track if form dirty
        # make this a new record
        self.currRec = self.createNewrefRec()
        self.setFormDirty(self,False)

        # set tab order
        QWidget.setTabOrder(self.dlistrefid, self.lnedtFilePath)
        QWidget.setTabOrder(self.lnedtFilePath, self.btnChooseFilePaths)
        QWidget.setTabOrder(self.btnChooseFilePaths, self.txtedtNotes)
        QWidget.setTabOrder(self.txtedtNotes, self.wdgtDetail[0][self.rowData])

        QWidget.setTabOrder(self.wdgtDetail[0][self.rowData], self.wdgtDetail[1][self.rowData])
        QWidget.setTabOrder(self.wdgtDetail[1][self.rowData], self.wdgtDetail[2][self.rowData])
        QWidget.setTabOrder(self.wdgtDetail[2][self.rowData], self.wdgtDetail[3][self.rowData])
        QWidget.setTabOrder(self.wdgtDetail[3][self.rowData], self.comboCompany)

        QWidget.setTabOrder(self.comboCompany, self.comboMode)
        QWidget.setTabOrder(self.comboMode, self.comboOrigin)
        QWidget.setTabOrder(self.comboOrigin, self.dtedPickupDt)

        QWidget.setTabOrder(self.dtedPickupDt, self.dtedETA)
        QWidget.setTabOrder(self.dtedETA, self.dtedDelivAppt)
        QWidget.setTabOrder(self.dtedDelivAppt, self.dtedLFD)
        QWidget.setTabOrder(self.dtedLFD, self.btnCommit)

        QWidget.setTabOrder(self.btnCommit, self.dlistrefid)

        self.retranslateUi()
    # __init__


    def retranslateUi(self):
        self.setWindowTitle(self.tr("References", None))
        self.lblFormName.setText(self.tr("References", None))

        self.btnCommit.setText(self.tr('Commit\nChanges',None))
        
        self.lblCompany.setText(self.tr("Company:"))
        self.lblMode.setText(self.tr("Frt Type:"))
        self.lblOrigin.setText(self.tr("Origin:"))
        self.lblDateHdr.setText(self.tr("Dates"))
        self.lblPickupDt.setText(self.tr("Pickup:"))
        self.lblETA.setText(self.tr("ETA:"))
        self.lblDelivAppt.setText(self.tr("Deliv Appt:"))
        self.lblLFD.setText(self.tr("LFD:"))
   # retranslateUi


    @Slot()
    def ChooseFiles(self):
        fyles, filt = QFileDialog.getOpenFileNames(self,'Choose Files',dir="W:\\Logistics\\Invoices")     #TODO: make dir a parm
        if fyles:
            self.currRec.FilePath = ','.join(fyles)
        
    def getRecordFromGoto(self) -> None:
        #TODO: check if dirty
        wdgtGoTo = self.dlistrefid

        slctd = wdgtGoTo.selectedItem()
        refEnterd = slctd['text']
        # id = wdgt.currentData()
        id = slctd['keys'][0] if len(slctd['keys']) else None
        if not id and refEnterd:
            # create new record?
            ans = QMessageBox.question(
                self, 
                "Create ref?", f'Reference {refEnterd} does not exist. Create it?',
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
                )
            if ans == QMessageBox.StandardButton.No:
                wdgtGoTo.undo()
                wdgtGoTo.setFocus()
                return
            else:
                newrec = self.createNewrefRec(
                    refID=str(refEnterd),     
                    saverec= True
                )
                id = newrec.pk
                # add this new HBL to the dlist
                wdgtGoTo.addChoices({id: refEnterd})
            #endif ans == QMessageBox.StandardButton.No
        # endif not id
        
        if id:
            self.getRecordfromdb(id)
    # getRecordFromGoto
    
    def dependentFieldEnable(self):
        for field, valu in self.formFields.items():
            wdgt, dependsOn = valu
            if field == 'ETA':
                # depends on HBL or Container
                wdgt.setEnabled(self.currRec.HBL is not None or self.currRec.Container is not None)
            elif dependsOn=='HBL':
                wdgt.setEnabled(self.currRec.HBL is not None)
            elif dependsOn=='Container':
                wdgt.setEnabled(self.currRec.Container is not None)
            #endif field/dependsOn
        # for every field
                


    ##########################################
    ########    Create

    def createNewrefRec(self, refID:str = None, saverec:bool = False) -> references:
        newRec = references(
            notes = '',
            )
        if refID: newRec.refName = refID
        
        if saverec:
            newRec.save()
        
        return newRec


    ##########################################
    ########    Read

    def getRecordfromdb(self, recid:int, createFlag:bool = False) -> int:
        self.currRec = references.objects.get(pk=recid)
        self.fillFormFromcurrRec()
        
        return self.currRec.pk
    # getRecordfromdb

    def fillFormFromcurrRec(self):
        cRec = self.currRec
    
        # set pk display
        self.lblRecID.setText(str(cRec.pk))

        for field, info in self.formFields.items():
            wdgt, linkFrom = info
            field_value = getattr(cRec, field, None)
            field_valueStr = field_value
            # transform values for foreign keys and lookups
            forgnKeys = {
                'id': cRec,
                'HBL': cRec.HBL, 
                'Invoice': cRec.Invoice, 
                'Container': cRec.Container, 
                'ShippingForm': cRec.ShippingForm, 
                'Company': cRec.HBL.Company if cRec.HBL else None, 
                'FreightType': cRec.HBL.FreightType if cRec.HBL else None, 
                'Origin': cRec.HBL.Origin if cRec.HBL else None,
                # 'PickupDt': None, 
                # 'ETA': None, 
                # 'DelivAppt': None, 
                # 'LFD': None,
                }
            if field in forgnKeys:
                field_valueStr = str(forgnKeys[field]) if forgnKeys[field] is not None else ''
            if field in ['PickupDt', 'ETA', 'DelivAppt', 'LFD']:
                field_value = getattr(getattr(cRec, linkFrom, None), field, None)
            
            # set wdgt value to field_value
            # must set value per widget type
            if any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
                wdgt.setText(field_valueStr)
            elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
                wdgt.setPlainText(field_valueStr)
            elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
                chNum = wdgt.findData(field_valueStr)
                if chNum == -1: 
                    wdgt.setCurrentText(field_valueStr)
                else:
                    wdgt.setCurrentIndex(chNum)
                #endif findData valid
            elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
                wdgt.setDate(field_value)
            # endif widget type test

        #endfor field in cRec
        
        if cRec.pk is None:
            self.setFormDirty(self, False)
        
    # fillFormFromcurrRec

    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        cRec = self.currRec
        dbField = wdgt.property('field')
        
        forgnKeys = [
            'HBL', 
            'Invoice', 
            'Container', 
            'ShippingForm', 
            ]
        specFldInfo = namedtuple('specFldInfo',['parentFld', 'wrttoObj', 'wrttoFld'])
        specialProcFlds = {
            'Company': specFldInfo('HBL', cRec.HBL, 'Company_id'), 
            'FreightType': specFldInfo('HBL', cRec.HBL, 'FreightType_id'), 
            'Origin': specFldInfo('HBL', cRec.HBL, 'Origin_id'),
            'PickupDt': specFldInfo('HBL', cRec.HBL, 'PickupDt'), 
            'ETA': specFldInfo('HBL', cRec.HBL, 'ETA'), 
            'DelivAppt': specFldInfo('Container', cRec.Container, 'DelivAppt'), 
            'LFD': specFldInfo('Container or HBL', cRec.Container if cRec.Container else cRec.HBL, 'LFD'),
            }
        wdgt_value = None
        
        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):  
            wdgt_value = wdgt.selectedItem()['keys'][0] if wdgt.selectedItem()['keys'] else None
        elif any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
            wdgt_value = wdgt.text()
        elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
            wdgt_value = wdgt.toPlainText()
        elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
            wdgt_value = wdgt.currentData()
        elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
            wdgt_value = wdgt.date().toPython()
        elif any([wdgt.inherits(tp) for tp in ['QCheckBox', ]]):
            wdgt_value = wdgt.isChecked()
        # endif widget type test

        if dbField in forgnKeys:
            dbField += '_id'
        
        if wdgt_value:
            if dbField in specialProcFlds:
                if dbField == 'Origin': breakpoint()
                specFld = specialProcFlds[dbField]
                if not specFld.wrttoObj:
                    print(f'{specFld.parentFld} must be provided before setting {dbField}\nMAKE ME A MsgBox!!!')
                    # wdgt.undo() - clear or undo depending on wdgt type
                    self.formFields[specFld.parentFld][0].setFocus()
                    return False
                # if not specFld.wrttoFld
                setattr(specFld.wrttoObj, specFld.wrttoFld, wdgt_value)
            else:
                setattr(cRec, dbField, wdgt_value)
            # if in specialProcFlds
            self.setFormDirty(wdgt, True)
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec = self.currRec
        newrec = (cRec is None)
        
        # There MUST be a refName, and it can't belong to another record
        if not cRec.refName:
            QMessageBox(QMessageBox.Icon.Critical, 'Must provide Ref Name','You must provide a Reference id!',
                QMessageBox.StandardButton.Ok, self).show()
            self.dlistrefid.setFocus()
            return
        existingrec = [R.pk for R in references.objects.filter(refName=cRec.refName)]
        if len(existingrec) and cRec.pk not in existingrec:
            QMessageBox(QMessageBox.Icon.Critical, 'ref Name Exists', f'ref Name {cRec.refName} exists in another record!',
                QMessageBox.StandardButton.Ok, self).show()
            self.dlistrefid.clear()
            self.dlistrefid.setFocus()
            return

        # check other traps later
        
        cRec.save()
        pk = cRec.pk
        self.lblRecID.setText(str(pk))

        if newrec:
            # add this record to self.gotoHBL.completer().model()
            self.dlistrefid.addChoices({pk: str(cRec.refName)})
            
        self.setFormDirty(self, False)


    ##########################################
    ########    Delete


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit']]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
        
        # disable fields dependent on others not set
        self.dependentFieldEnable()
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')

##############################################################
##############################################################
##############################################################

