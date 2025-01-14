from typing import Dict, List, Any

from PySide6.QtCore import (QCoreApplication,
    Qt, Slot,
    QDate,
    QMetaObject, QObject, QPoint, QRect,
    QStringListModel, QModelIndex
    )
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
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
from incShip.models import HBL, Invoices, ShippingForms, Containers, references, reference_ties, all_references
from forms import IncShipAppchoiceWidgets, Invoice_singleForm
from forms import std_windowsize
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
        self.setWindowTitle(QCoreApplication.translate("Frame", u"Test Window 2", None))
        self.label.setText(QCoreApplication.translate("Frame", u"This is test label 1", None))
    # retranslateUi
# class Test02

class Test03():
    def __init__(self):
        # just wanna debug ...
        pass
    def setProperty(self, dummy1, dummy2):
        pass

class refsForm(QWidget):
    _linkedTables = {
        reference_ties.refTblChoices.Invoices      : Invoices,
        reference_ties.refTblChoices.ShippingForms : ShippingForms,
        reference_ties.refTblChoices.HBL           : HBL,
        reference_ties.refTblChoices.Containers    : Containers,
    }

    currRec:reference_ties = None
    linkedRecs:Dict[reference_ties.refTblChoices, Any] = { tbl: None for tbl in _linkedTables}
    
    columnHBL, columnContainers, columnShipForms, columnInvoices = range(4)
        # actually used as column numbers in a QGridLayout, so as much as I want to, I can't set
        # reference_ties.refTblChoices.HBL, reference_ties.refTblChoices.Containers, reference_ties.refTblChoices.ShippingForms, reference_ties.refTblChoices.Invoices
    rowLabel, rowAddBtn, rowRefList = range(3)

    def __init__(self, parent:QWidget = None):
        super().__init__(parent)

        if not self.objectName():
            self.setObjectName(u"Form")
        # self.resize(std_windowsize)
        self.resize(std_windowsize.width(), std_windowsize.height()) # this is a temporary fix
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        thisWindowsize = self.size()

        ### FormHdr

        # self.layoutwidgetFormHdr = QWidget()
        self.layoutFormHdr = QVBoxLayout(self.layoutwidgetFormHdr)
        
        self.lblFormName = QLabel(self)
        wdgt = self.lblFormName
        wdgt.setObjectName(u"lblFormName")
        font1 = QFont()
        font1.setFamilies([u"Century Gothic"])
        font1.setPointSize(24)
        wdgt.setFont(font1)
        wdgt.setFrameShape(QFrame.Shape.Panel)
        wdgt.setFrameShadow(QFrame.Shadow.Raised)
        wdgt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wdgt.setWordWrap(True)
        self.layoutFormHdr.addWidget(wdgt)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addSpacing(10)

        ### FormMainTop

        # self.layoutwidgetFormMainTop = QWidget(self)
        self.layoutFormMainTop = QHBoxLayout(self.layoutwidgetFormMainTop)
        self.layoutFormMainTopLeft = QFormLayout(self.layoutwidgetFormMainTop)
        self.layoutFormMainTopRight = QVBoxLayout(self.layoutwidgetFormMainTop)
        self.layoutFormMainTop.addLayout(self.layoutFormMainTopLeft)
        self.layoutFormMainTop.addLayout(self.layoutFormMainTopRight)
        
        self.lblRecID = QLabel()
        self.lblRecID.setProperty('field', 'id')
        refid_codeblock = True      # I do this to emphasize a logical codeblock unit
        if refid_codeblock:
            # self.lWidg_refidBlock = QWidget()
            self.lyout_refidBlock = QHBoxLayout(self.lWidg_refidBlock)
            refdict = {rec.pk: rec.emaildatefrom_or_filelocation for rec in references.objects.all()}
            self.dlistrefid = cDataList(refdict,parent=self.lWidg_refidBlock)
            self.dlistrefid.setProperty('field', 'emaildatefrom_or_filelocation')
            self.dlistrefid.editingFinished.connect(self.getRecordFromGoto)
            self.lblrefidExpln = QLabel(self.lWidg_refidBlock)
            self.lblrefidExpln.setText(self.tr('(if the ref id you enter doesn\'t exist, it will be created)'))
            self.lblrefidExpln.setWordWrap()
            self.lyout_refidBlock.addWidget(self.dlistrefid)
            self.lyout_refidBlock.addWidget(self.lblrefidExpln)
        FilePath_codeblock = True      # I do this to emphasize a logical codeblock unit
        if FilePath_codeblock:
            # self.lWidg_FilePathBlock = QWidget()
            self.lyout_FilePathBlock = QHBoxLayout(self.lWidg_FilePathBlock)
            self.lnedtFilePath = QLineEdit(self.lWidg_FilePathBlock)
            self.lnedtFilePath.setProperty('field', 'FilePath')
            self.lnedtFilePath.editingFinished.connect(lambda: self.changeField(self.lnedtFilePath))
            self.btnChooseFilePaths = QPushButton(self.tr('Choose Files'),self.lWidg_FilePathBlock)
            self.btnChooseFilePaths.clicked.connect(lambda: pleaseWriteMe(self, 'Choose File Path - use QFileDialog'))
            self.lyout_FilePathBlock.addWidget(self.lnedtFilePath)
            self.lyout_FilePathBlock.addWidget(self.btnChooseFilePaths)
        self.txtedtNotes = QTextEdit(); 
        self.txtedtNotes.setProperty('field', 'notes')
        self.txtedtNotes.textChanged.connect(lambda: self.changeField(self.txtedtNotes))

        self.layoutFormMainTopLeft.addRow('reference id', self.lyout_refidBlock)
        self.layoutFormMainTopLeft.addRow('File Refs', self.lyout_FilePathBlock)
        self.layoutFormMainTopLeft.addRow(self.tr('notes'), self.txtedtNotes)

        self.layoutFormMainTopRight.addWidget(self.lblRecID)
        self.layoutFormMainTopRight.addSpacing(20)
        self.btnCommit = QPushButton(self.layoutwidgetFormMainTop)
        self.btnCommit.clicked.connect(lambda: self.writeRecord())
        self.layoutFormMainTopRight.addWidget(self.btnCommit)

        self.layoutForm.addLayout(self.layoutFormMainTop)
        self.layoutForm.addSpacing(10)

        ### FormMainDetail

        # self.layoutwidgetFormMainDetail = QWidget(self)
        self.layoutFormMainDetail = QGridLayout()
        
        columnHBL, columnContainers, columnShipForms, columnInvoices \
            = self.columnHBL, self.columnContainers, self.columnShipForms, self.columnInvoices
        rowLabel, rowAddBtn, rowRefList \
            = self.rowLabel, self.rowAddBtn, self.rowRefList
        #
        self.wdgtDetail = [[None for row in (rowLabel, rowAddBtn, rowRefList)] for col in (columnHBL, columnContainers, columnShipForms, columnInvoices)]
        self.wdgtDetail[columnHBL][rowLabel] = QLabel('HBL', self)
        self.wdgtDetail[columnContainers][rowLabel] = QLabel(self.tr('Containers'), self)
        self.wdgtDetail[columnShipForms][rowLabel] = QLabel(self.tr('Shipping Forms'), self)
        self.wdgtDetail[columnInvoices][rowLabel] = QLabel(self.tr('Invoices'), self)
        #
        self.wdgtDetail[columnHBL][rowAddBtn] = QPushButton(self.tr('Add HBL', self))
        self.wdgtDetail[columnHBL][rowAddBtn].clicked.connect(lambda: pleaseWriteMe(self, 'Add HBL'))                   # self.addDetail(reference_ties.refTblChoices.HBL)
        self.wdgtDetail[columnContainers][rowAddBtn] = QPushButton(self.tr('Add Containers', self))
        self.wdgtDetail[columnContainers][rowAddBtn].clicked.connect(lambda: pleaseWriteMe(self, 'Add Containers'))     # self.addDetail(reference_ties.refTblChoices.Containers)
        self.wdgtDetail[columnShipForms][rowAddBtn] = QPushButton(self.tr('Add Ship Forms', self))
        self.wdgtDetail[columnShipForms][rowAddBtn].clicked.connect(lambda: pleaseWriteMe(self, 'Add Ship Forms'))      # self.addDetail(reference_ties.refTblChoices.ShippingForms)
        self.wdgtDetail[columnInvoices][rowAddBtn] = QPushButton(self.tr('Add Invoices', self))
        self.wdgtDetail[columnInvoices][rowAddBtn].clicked.connect(lambda: pleaseWriteMe(self, 'Add Invoices'))         # self.addDetail(reference_ties.refTblChoices.Invoices)
        #
        self.wdgtDetail[columnHBL][rowRefList] = QListWidget(self)
        self.wdgtDetail[columnContainers][rowRefList] = QListWidget(self)
        self.wdgtDetail[columnShipForms][rowRefList] = QListWidget(self)
        self.wdgtDetail[columnInvoices][rowRefList] = QListWidget(self)

        for row in (rowLabel, rowAddBtn, rowRefList):
            for col in (columnHBL, columnContainers, columnShipForms, columnInvoices):
                self.layoutFormMainDetail.addWidget(self.wdgtDetail[col][row])
        self.layoutForm.addLayout(self.layoutFormMainDetail)

        # track if form dirty
        # self.setFormDirty(self, False)
        # make this a new record
        self.currRec = self.createNewrefRec()
        self.setFormDirty(self,False)

        self.retranslateUi()
    # __init__


    #TODO: Move to init ??
    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("Form", u"References", None))

        self.lblNotes.setText(QCoreApplication.translate("Form", u"Notes", None))
        self.lblFormName.setText(QCoreApplication.translate("Form", u"References", None))

        self.btnCommit.setText(QCoreApplication.translate('Form','Commit\nChanges',None))
   # retranslateUi

    # def newInvWidgetThisHBL(self) -> QWidget:
    #     return Invoice_singleForm(HBLRec=self.currRec)

    def getRecordFromGoto(self) -> None:
        #TODO: check if dirty
        wdgtGoTo = self.dlistrefid

        slctd = wdgtGoTo.selectedItem()
        refEnterd = slctd['text']
        # id = wdgt.currentData()
        id = slctd['keys'][0] if len(slctd['keys']) else None
        if not id and refEnterd:
            # wdgtGoTo.undo()

            # create new HBL record
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


    ##########################################
    ########    Create

    def addDetail(self, sectnDetail:reference_ties.refTblChoices):
        blankFillIns = {
            reference_ties.refTblChoices.Containers:    ('Container', 'Container Number', Containers, 'ContainerNumber'),
            reference_ties.refTblChoices.HBL:           ('HBL', 'HBL', HBL, 'HBLNumber'),
            reference_ties.refTblChoices.ShippingForms: ('Ship Form', 'Shipping Form', ShippingForms, 'id_SmOffFormNum'),
            reference_ties.refTblChoices.Invoices:      ('Invoice', 'Invoice', Invoices, 'InvoiceNumber'),
        }
        input_str, ok = QInputDialog.getText(self,
            f'Enter {blankFillIns[sectnDetail][0]}s', f'Enter {blankFillIns[sectnDetail][1]}s to add, separated by commas',
            )
        if not ok:
            return
        input_list = [x for x in ''.join(input_str.split()).split(',')]
        for vlu in input_list:
            if sectnDetail==reference_ties.refTblChoices.ShippingForms: vlu = int(vlu)
            vluRec = blankFillIns[sectnDetail][2].objects.filter(**{blankFillIns[sectnDetail][3]: vlu}).last()
            # check if not exists
            if not vluRec:
                # offer to add
                ans = QMessageBox.question(self, 
                    f'Create {blankFillIns[sectnDetail][0]}?', 
                    f'{blankFillIns[sectnDetail][1]} {vlu} does not exist. Create it?\n(if you do, don\'t forget to edit it)',
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
                if ans == QMessageBox.StandardButton.No:
                    continue
                else:
                    vluRec = blankFillIns[sectnDetail][2].objects.create(incoterm='', notes='', **{blankFillIns[sectnDetail][3]: vlu} )
                #endif ans == No
            # endif not sfRec
            
            # add sf to reference_ties
            reference_ties.objects.create(
                email = self.currRec,
                table_ref = sectnDetail,
                record_ref = vluRec.pk
            )
        
        # rebuild section list
        self.fillFormFromlinkedrefs()
    # addShipFmToHBL

    def createNewrefRec(self, refID:str = None, saverec:bool = False) -> references:
        newRec = references(
            notes = '',
            )
        if refID: newRec.emaildatefrom_or_filelocation = refID
        
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
        RESTARTHERE
        cRec = self.currRec
    
        # set pk display
        self.lblRecID.setText(str(cRec.pk))

        for field in cRec._meta.get_fields():
            # special cases: ShippingForms, POList, containers, invoices:
            if field.name in ['ShippingForms', 'POList', 'Invoices', 'Containers', 'reference_ties']:
                continue

            field_value = getattr(cRec, field.name, None)
            field_valueStr = field_value
            # transform values for foreign keys and lookups
            forgnKeys = {
                'id': cRec,
                'Company': cRec.Company,
                'FreightType': cRec.FreightType,
                'Origin': cRec.Origin,
                'Quote': cRec.Quote,
                }
            if field.name in forgnKeys:
                field_valueStr = str(forgnKeys[field.name])
            
            for wdgt in self.findChildren(QWidget):
                if wdgt.property('field') == field.name:
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

                    break   # we found the widget for this field; we don't need to test other widgets
                            # move on to the next field
                # endif wdgt field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
        
        if cRec.pk is None:
            # there are no linked recs yet, and most of the below will bomb
            self.setFormDirty(self, False)
            return
        
        # get linked recs
        # _linkedTables = ['ShippingForms', 'PO', 'Invoices', 'Containers', 'reference_ties']
        self.fillFormFromlinkedrefs()
        
        self.fillFormFromlinkedPO()
        
        self.fillFormFromlinkedInvoices()

        self.fillFormFromlinkedContainers()

        self.fillFormFromlinkedrefs()
        
        self.setFormDirty(self, False)
    # fillFormFromcurrRec

    def fillFormFromlinkedPO(self):
        cRec = self.currRec
        self.linkedRecs['PO'] = cRec.POList.all()
        self.listWidgetPO.clear()
        self.listWidgetPO.addItems( [rec.PONumber for rec in self.linkedRecs['PO']] )
    
    def fillFormFromlinkedContainers(self):
        cRec = self.currRec
        self.linkedRecs['Containers'] = Containers.objects.filter(HBL=cRec)
        qmodel = QModelContainers({'HBL': cRec})
        self.tblViewContainers.setModel(qmodel)
    
    def fillFormFromlinkedInvoices(self):
        cRec = self.currRec
        self.linkedRecs['Invoices'] = Invoices.objects.filter(HBL=cRec)
        qmodel = QModelInvoices({'HBL': cRec})
        self.tblViewInvoices.setModel(qmodel)
        self.InvcRecSet.init_recSet()
        for rec in self.linkedRecs['Invoices']:
            wdgtInv = Invoice_singleForm(InvRec=rec)
            self.InvcRecSet.addWidget(wdgtInv)
    
    def fillFormFromlinkedrefs(self):
        cRec = self.currRec
        self.linkedRecs['ShippingForms'] = cRec.ShippingForms.all()
        self.listWidgetShpFms.clear()
        self.listWidgetShpFms.addItems( [str(rec.id_SmOffFormNum) for rec in self.linkedRecs['ShippingForms']] )
    
    def fillFormFromlinkedrefs(self):
        cRec = self.currRec
        # fill references
        Q1 = Q(table_ref=refs.refTblChoices.Containers) & Q(record_ref__in=self.linkedRecs['Containers'].values_list('pk'))
        Q2 = Q(table_ref=refs.refTblChoices.HBL) & Q(record_ref=cRec.pk)
        Q3 = Q(table_ref=refs.refTblChoices.Invoices) & Q(record_ref__in=self.linkedRecs['Invoices'].values_list('pk'))
        Q4 = Q(table_ref=refs.refTblChoices.ShippingForms) & Q(record_ref__in=self.linkedRecs['ShippingForms'].values_list('pk'))
        reflist = all_references().filter(Q1 | Q2 | Q3 | Q4)
        self.linkedRecs['reference_ties'] = reflist
        qmodel = QModelrefs(reflist)
        self.tblViewrefs.setModel(qmodel)
    
    
    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        forgnKeys = {   
            'Company',
            'FreightType',
            'Origin',
            'Quote',
            }
        cRec = self.currRec
        dbField = wdgt.property('field')
        
        wdgt_value = None
        
        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):  # I hope I hope I hope
            wdgt_value = wdgt.selectedItem()['keys'][0]
        if any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
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
            # forgnModel:Model = getattr(cRec,dbField).related_model
            # print(forgnModel)   #debugging
            # wdgt_value = forgnModel.objects.get(pk=wdgt_value)
            dbField += '_id'
        
        if wdgt_value:
            setattr(cRec, dbField, wdgt_value)
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
        
        # There MUST be a HBLNumber, and it can't belong to another record
        if not cRec.HBLNumber:
            QMessageBox(QMessageBox.Icon.Critical, 'Must provide HBL Number','You must provide a HBL Number!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedHBLNumber.setFocus()
            return
        existingrec = [R.pk for R in HBL.objects.filter(HBLNumber=cRec.HBLNumber)]
        if len(existingrec) and cRec.pk not in existingrec:
            QMessageBox(QMessageBox.Icon.Critical, 'HBL Number Exists', f'HBL {cRec.HBLNumber} exists in another record!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedHBLNumber.clear()
            self.lnedHBLNumber.setFocus()
            return

        # check other traps later
        
        cRec.save()
        pk = cRec.pk
        self.lblRecID.setText(str(pk))
        
        self.gotoHBL.setText(cRec.HBLNumber)

        if newrec:
            # add this record to self.gotoHBL.completer().model()
            self.gotoHBL.addChoices({pk: str(cRec.HBLNumber)})
            
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
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')

##############################################################
##############################################################
##############################################################

