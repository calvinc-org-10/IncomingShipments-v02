from typing import (Dict, List, Any, )

from django import db
from django.db.backends.utils import CursorWrapper

from PySide6.QtCore import (Qt, QObject,
    Signal, Slot, 
    QAbstractTableModel, QModelIndex, )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( QStyle, 
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, 
    QTableView, QHeaderView,
    QDialog, QMessageBox, QFileDialog, QDialogButtonBox,
    QLabel, QLCDNumber, QLineEdit, QTextEdit, QPushButton, QCheckBox, QComboBox, 
    QRadioButton, QGroupBox, QButtonGroup, 
    QSizePolicy, 
    )

# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 

from menuformname_viewMap import FormNameToURL_Map

from django.db import transaction
from django.db.models import QuerySet

from .dbmenulist import (MenuRecords, newgroupnewmenu_menulist, newmenu_menulist, )
from sysver import sysver
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .models import (menuItems, menuGroups, )
from .utils import (cComboBoxFromDict, QRawSQLTableModel, UnderConstruction_Dialog,
    Excelfile_fromqs, pleaseWriteMe, dictfetchall, 
    )

# copied from cMenu - if you change it here, change it there
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)


fontFormTitle = QFont()
fontFormTitle.setFamilies([u"Copperplate Gothic"])
fontFormTitle.setPointSize(24)


class QWGetSQL(QWidget):
    runSQL = Signal(str)    # Emitted with the SQL string when run is clicked
    cancel = Signal()       # Emitted when cancel is clicked    
    
    def __init__(self, parent = None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = QLabel()
        self.lblFormName.setFont(fontFormTitle)
        self.lblFormName.setFrameShape(QFrame.Shape.Panel)
        self.lblFormName.setFrameShadow(QFrame.Shadow.Raised)
        self.lblFormName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblFormName.setWordWrap(True)
        self.lblFormName.setText(self.tr('Enter SQL'))
        self.setWindowTitle(self.tr('Enter SQL'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)
        
        # main area for entering SQL
        self.layoutFormMain = QFormLayout()
        self.txtedSQL = QTextEdit()
        self.layoutFormMain.addRow(self.tr('SQL statement'), self.txtedSQL)
        
        # run/Cancel buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonRunSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.Computer), self.tr('Run SQL') ) 
        self.buttonRunSQL.clicked.connect(self._on_run_sql_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonRunSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Cancel') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        horzline2 = QFrame()
        horzline2.setFrameShape(QFrame.Shape.HLine)
        horzline2.setFrameShadow(QFrame.Shadow.Sunken)
        
        # status message
        self.lblStatusMsg = QLabel()
        self.lblStatusMsg.setText('\n\n')
        
        # Hints
        self.lblHints = QLabel()
        self.lblHints.setText('db hints will go here ...')
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addWidget(self.lblStatusMsg)
        self.layoutForm.addWidget(horzline2)
        self.layoutForm.addWidget(self.lblHints)
        
    def _on_run_sql_clicked(self):
        # Emit the runSQL signal with the text from the editor.
        sql_text = self.txtedSQL.toPlainText()
        self.runSQL.emit(sql_text)

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.cancel.emit()        

    def closeEvent(self, event):
        self.cancel.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)

class QWShowSQL(QWidget):
    ReturnToSQL = Signal()
    closeMe = Signal()
    closeBoth = Signal()
    
    def __init__(self, origSQL:str, rows:List[Dict[str, Any]], colNames:str|List[str], parent:QWidget = None):
        super().__init__(parent)

        # save incoming for future use if needed
        self.origSQL = origSQL
        self.rows = rows
        self.colNames = colNames

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = QLabel()
        self.lblFormName.setFont(fontFormTitle)
        self.lblFormName.setFrameShape(QFrame.Shape.Panel)
        self.lblFormName.setFrameShadow(QFrame.Shadow.Raised)
        self.lblFormName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblFormName.setWordWrap(True)
        self.lblFormName.setText(self.tr('SQL Results'))
        self.setWindowTitle(self.tr('SQL Results'))
        
        self.layoutFormSQLDescription = QFormLayout()
        self.lblOrigSQL = QLabel()
        self.lblOrigSQL.setText(origSQL)
        self.lblnRecs = QLabel()
        self.lblnRecs.setText(f'{len(rows)}')
        self.lblcolNames = QLabel()
        self.lblcolNames.setText(str(colNames))
        self.layoutFormSQLDescription.addRow('SQL Entered:', self.lblOrigSQL)
        self.layoutFormSQLDescription.addRow('rows affctd:', self.lblnRecs)
        self.layoutFormSQLDescription.addRow('cols:', self.lblcolNames)
        
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)
        self.layoutFormHdr.addWidget(self.lblOrigSQL)
        self.layoutFormHdr.addWidget(self.lblnRecs)
        self.layoutFormHdr.addWidget(self.lblcolNames)

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        
        resultModel = QRawSQLTableModel(rows, colNames, self.parent())
        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(resultModel)
        self.layoutFormMain.addWidget(resultTable)
        
        #  buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonGetSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), self.tr('Back to SQL') ) 
        self.buttonGetSQL.clicked.connect(self._return_to_sql)
        self.layoutFormActionButtons.addWidget(self.buttonGetSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonDLResults = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), self.tr('D/L Results') ) 
        self.buttonDLResults.clicked.connect(self.DLResults)
        self.layoutFormActionButtons.addWidget(self.buttonDLResults, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Close') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormSQLDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addLayout(self.layoutFormActionButtons)

    @Slot()
    def DLResults(self):
        ExcelFileNamePrefix = "SQLresults"
        # Excel_qdict = [{self.colNames[x]:cRec[x] for x in range(len(self.colNames))} for cRec in self.rows]
        Excel_qdict = self.rows
        xlws = Excelfile_fromqs(Excel_qdict)
        filName, _ = QFileDialog.getSaveFileName(self, 
            "Enter Spreadsheet File Name",
            selectedFilter=f'{ExcelFileNamePrefix}*'
        )
        if filName:
            xlws.save(filName)     
        
    def _return_to_sql(self):
        self.ReturnToSQL.emit()

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.closeBoth.emit()        

    def closeEvent(self, event):
        self.closeMe.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)
    
class cMRunSQL(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.inputSQL:str = None
        self.rows:CursorWrapper = None
        self.colNames:str|List[str] = None
        self.wndwAlive:Dict[str,bool] = {}
        
        self.wndwGetSQL = QWGetSQL(parent)
        self.wndwGetSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwGetSQL.runSQL.connect(self.rawSQLexec)
        self.wndwGetSQL.cancel.connect(self._on_cancel)
        self.wndwAlive['Get'] = True
        self.wndwGetSQL.destroyed.connect(lambda: self.wndwDest('Get'))
        
        self.wndwShowSQL = None        # will be redefined later

    def wndwDest(self, whichone:str):
        self.wndwAlive[whichone] = False
        
    def show(self):
        self.wndwGetSQL.show()
        
    @Slot(str)
    def rawSQLexec(self, inputSQL:str):
        sqlerr = None
        with db.connection.cursor() as djngocursor:
            try:
                djngocursor.execute(inputSQL)
            except Exception as err:
                sqlerr = err
            if not sqlerr:
                colNames = []
                if djngocursor.description:
                    colNames = [col[0] for col in djngocursor.description]
                    rows = dictfetchall(djngocursor)
                else:
                    colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
                    rows = []
                #endif cursor.description

                self.inputSQL = inputSQL        # preserve for later use
                self.rows = rows                # preserve for later use
                self.colNames = colNames        # preserve for later use
                self.rawSQLshow()
            else:  
                # show sqlerr in self.wndwGetSQL
                self.wndwGetSQL.lblStatusMsg.setText(f'ERROR: {sqlerr}')
                # self.wndwGetSQL.repaint()
            #endif not sqlerr
        #end with

    def rawSQLshow(self):
        self.wndwShowSQL = QWShowSQL(self.inputSQL, self.rows, self.colNames, self.parent())
        self.wndwShowSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwShowSQL.ReturnToSQL.connect(self._ShowToGetSQL)
        self.wndwShowSQL.closeBoth.connect(self._on_cancel)

        self.wndwAlive['Show'] = True
        self.wndwShowSQL.destroyed.connect(lambda: self.wndwDest('Show'))


        self.wndwGetSQL.hide()
        self.wndwShowSQL.show()

    @Slot()
    def _ShowToGetSQL(self):
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        self.wndwGetSQL.show()
        
    @Slot()
    def _on_cancel(self):
        # Handle the cancellation by closing both windows.
        self._close_all()

    def _close_all(self):
        # Close the child widget if it exists.
        if self.wndwAlive.get('Get'):
            self.wndwGetSQL.close()
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        # Close this widget (cMRunSQL) as well.
        self.close()

########################################
########################################

def FormBrowse(parntWind, formname):
    urlIndex = 0
    viewIndex = 1

    # theForm = 'Form ' + formname + ' is not built yet.  Calvin needs more coffee.'
    theForm = None
    # formname = formname.lower()
    if formname in FormNameToURL_Map:
        if FormNameToURL_Map[formname][urlIndex]:
            # figure out how to repurpose this later
            # url = FormNameToURL_Map[formname][urlIndex]
            # try:
            #     theView = resolve(reverse(url)).func
            #     urlExists = True
            # except (Resolver404, NoReverseMatch):
            #     urlExists = False
            # # end try
            # if urlExists:
            #     theForm = theView(req)
            # else:
            #     formname = f'{formname} exists but url {url} '
            # #endif
            pass
        elif FormNameToURL_Map[formname][viewIndex]:
            try:
                fn = FormNameToURL_Map[formname][viewIndex]
                viewExists = True
            except NameError:
                viewExists = False
            #end try
            if viewExists:
                # dtheForm = fn(parntWind)
                theForm = fn()
            else:  
                formname = f'{formname} exists but view {FormNameToURL_Map[formname][viewIndex]}'
            #endif
    if not theForm:
        formname = f'Form {formname} is not built yet.  Calvin needs more coffee.'
        # print(formname)
        UnderConstruction_Dialog(parntWind, formname).show()
    else:
        # print(f'about to show {theForm}')
        # theForm.show()
        # print(f'done showing')
        return theForm
    # endif

    # must be rendered if theForm came from a class-based-view
    # if hasattr(theForm,'render'): theForm = theForm.render()
    # return theForm

def ShowTable(parntWind, tblname):
    # showing a table is nothing more than another form
    return FormBrowse(parntWind,tblname)

#####################################################
#####################################################

class cWidgetMenuItem(QWidget):
    def __init__(self, menuitmRec:menuItems, parent:QWidget = None):
        super().__init__(parent)
        
        self.setObjectName('cWidgetMenuItem')
        
        self.currRec = menuitmRec
        
        # self.resize(780, 190)
        font = QFont()
        font.setPointSize(8)
        self.setFont(font)

        self.layoutFormMain = QVBoxLayout(self)
        self.layoutFormMain.setContentsMargins(1,1,1,1)

        ##
        self.layoutFormLine1 = QHBoxLayout()
        
        self.lblOptionNumber = QLabel(self)
        self.lblOptionNumber.setText(self.tr('Option Number '))
        self.lnedtOptionNumber = QLineEdit(self)
        self.lnedtOptionNumber.setProperty('field', 'OptionNumber')
        self.lnedtOptionNumber.setProperty('noedit', True)
        self.lnedtOptionNumber.setReadOnly(True)
        self.lnedtOptionNumber.setFrame(False)
        self.lnedtOptionNumber.setMaximumWidth(25)
        self.lnedtOptionNumber.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.lblOptionText = QLabel(self)
        self.lblOptionText.setText(self.tr('OptionText: '))
        self.lnedtOptionText = QLineEdit(self)
        self.lnedtOptionText.setProperty('field', 'OptionText')
        self.lnedtOptionText.editingFinished.connect(lambda: self.changeField(self.lnedtOptionText))

        self.layoutTopLine = QHBoxLayout()
        self.chkbxTopLine = QCheckBox(self.tr('Top Line'), self)
        self.chkbxTopLine.setProperty('field', 'TopLine')
        self.chkbxTopLine.checkStateChanged.connect(lambda newstate: self.changeField(self.chkbxTopLine))
        self.lnedtTopLine = QLineEdit(self)
        self.lnedtTopLine.setProperty('field', 'TopLine')
        self.lnedtTopLine.setProperty('noedit', True)
        self.lnedtTopLine.setReadOnly(True)
        self.lnedtTopLine.setFrame(False)
        self.lnedtTopLine.setMaximumWidth(40)
        self.lnedtTopLine.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.layoutTopLine.addWidget(self.lnedtTopLine)
        self.layoutTopLine.addWidget(self.chkbxTopLine)

        self.layoutBottomLine = QHBoxLayout()
        self.chkbxBottomLine = QCheckBox(self.tr('Btm Line'), self)
        self.chkbxBottomLine.setProperty('field', 'BottomLine')
        self.chkbxBottomLine.checkStateChanged.connect(lambda newstate: self.changeField(self.chkbxBottomLine))
        self.lnedtBottomLine = QLineEdit(self)
        self.lnedtBottomLine.setProperty('field', 'BottomLine')
        self.lnedtBottomLine.setProperty('noedit', True)
        self.lnedtBottomLine.setReadOnly(True)
        self.lnedtBottomLine.setFrame(False)
        self.lnedtBottomLine.setMaximumWidth(40)
        self.lnedtBottomLine.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.layoutBottomLine.addWidget(self.lnedtBottomLine)
        self.layoutBottomLine.addWidget(self.chkbxBottomLine)

        self.layoutFormLine1.addWidget(self.lblOptionNumber)
        self.layoutFormLine1.addWidget(self.lnedtOptionNumber)
        # self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addWidget(self.lblOptionText)
        self.layoutFormLine1.addWidget(self.lnedtOptionText)
        # self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addLayout(self.layoutTopLine)
        self.layoutFormLine1.addLayout(self.layoutBottomLine)

        ##

        self.layoutFormLine2 = QHBoxLayout()

        self.lblCommand = QLabel(self)
        self.lblCommand.setText(self.tr('Command: '))
        self.cmbobxCommand = cComboBoxFromDict(vars(COMMANDNUMBER), self)
        self.cmbobxCommand.setProperty('field', 'Command')
        self.cmbobxCommand.activated.connect(lambda: self.changeField(self.cmbobxCommand))

        self.lblArgument = QLabel(self)
        self.lblArgument.setText(self.tr('Argument: '))
        self.lnedtArgument = QLineEdit(self)
        self.lnedtArgument.setProperty('field', 'Argument')
        self.lnedtArgument.editingFinished.connect(lambda: self.changeField(self.lnedtArgument))

        self.lblPWord = QLabel(self)
        self.lblPWord.setText(self.tr('Password: '))
        self.lnedtPWord = QLineEdit(self)
        self.lnedtPWord.setProperty('field', 'PWord')
        self.lnedtPWord.editingFinished.connect(lambda: self.changeField(self.lnedtPWord))

        self.layoutFormLine2.addWidget(self.lblCommand)
        self.layoutFormLine2.addWidget(self.cmbobxCommand)
        # self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.lblArgument)
        self.layoutFormLine2.addWidget(self.lnedtArgument)
        # self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.lblPWord)
        self.layoutFormLine2.addWidget(self.lnedtPWord)

        ##
        
        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(self.writeRecord)
        # self.layoutFormLine2.addSpacing(5)
        self.layoutFormLine2.addWidget(self.btnCommit)

        self.lblReminders = QLabel(self.tr(' *** ADD REMOVE / MOVE / COPY ***'))
        # remove button
        # move / copy

        self.layoutFormMain.addLayout(self.layoutFormLine1)
        self.layoutFormMain.addLayout(self.layoutFormLine2)
        self.layoutFormMain.addWidget(self.lblReminders)
        
        self.fillFormFromcurrRec()

    # __init__

    ##########################################
    ########    Create

    # this widget doesn't create new records

    ##########################################
    ########    Read

    def fillFormFromcurrRec(self):
        cRec:menuItems = self.currRec
        
        # move to class var?
        forgnKeys = {
            'id': cRec if cRec else '',
            'MenuGroup': cRec.MenuGroup if cRec else '',
            }
        # move to class var?
        valu_transform_flds = {
        }
        for field in cRec._meta.get_fields():
            field_value = getattr(cRec, field.name, None)
            field_valueStr = str(field_value)
            if field.name in forgnKeys:
                field_valueStr = str(forgnKeys[field.name])
            if field.name in valu_transform_flds:
                field_valueStr = valu_transform_flds[field.name][0](field_value)
            
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
                    elif any([wdgt.inherits(tp) for tp in ['QCheckBox', ]]):
                        wdgt.setChecked(field_value if isinstance(field_value,bool) else False)
                    # endif widget type test

                    break   # we found the widget for this field; we don't need to keep testing widgets
                # endif widget field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
        
        # exception to the rule; the two chekbox YES/No exposewrs
        wdgt = self.lnedtTopLine
        wdgt.setText('YES' if getattr(cRec, wdgt.property('field'), False) else 'NO') 
        wdgt = self.lnedtBottomLine
        wdgt.setText('YES' if getattr(cRec, wdgt.property('field'), False) else 'NO') 
        
        self.setFormDirty(self, False)
    # fillFormFromRec


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
        }
        cRec:menuItems = self.currRec
        dbField = wdgt.property('field')

        wdgt_value = None

        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):  # I hope I hope I hope
            kees = wdgt.selectedItem()['keys']
            wdgt_value = kees[0] if kees else wdgt.text()
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
        if dbField in valu_transform_flds:
            wdgt_value = valu_transform_flds[dbField][1](wdgt_value)

        if wdgt_value or isinstance(wdgt_value,bool):
            setattr(cRec, dbField, wdgt_value)
            self.setFormDirty(wdgt, True)

            # exception to the rule; the two chekbox YES/No exposewrs
            specialwdgt = self.lnedtTopLine
            if dbField == specialwdgt.property('field'):
                specialwdgt.setText('YES' if getattr(cRec, specialwdgt.property('field'), False) else 'NO') 
            specialwdgt = self.lnedtBottomLine
            if dbField == specialwdgt.property('field'):
                specialwdgt.setText('YES' if getattr(cRec, specialwdgt.property('field'), False) else 'NO') 
        
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    @Slot()
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:menuItems = self.currRec
        
        # check other traps later
        
        cRec.save()
        pk = cRec.pk
                    
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    def rmvMenuOption(self):
        ...
        (mGrp, mnu, mOpt) = (self.currRec.MenuGroup, self.currRec.MenuID, self.currRec.OptionNumber)
        
        # verify delete
        
        # remove from db
        if self.currRec.pk:
            self.currRec.delete()
        
        # replace with an empty record
        self.currRec = menuItems(
            MenuGroup = mGrp,
            MenuID = mnu,
            OptionNumber =mOpt,
            )


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        if wdgt.property('noedit'):
            return
        
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')


    ##########################################
    ########    Widget-responding procs
    
    def copyMenuOption(self, moveit=False):
        ...

#############################################
#############################################


class cEditMenu(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    
    # don't try to do this here - QWidgets cannot be created before QApplication
    # menuScreen: QWidget = QWidget()
    # menuLayout: QGridLayout = QGridLayout()
    # menuButton: Dict[int, QPushButton] = {}

    class wdgtmenuITEM(cWidgetMenuItem):
        def __init__(self, menuitmRec, parent = None):
            super().__init__(menuitmRec, parent)
            
    class cEdtMnuDlgGetNewMenuGroupInfo(QDialog):
        def __init__(self, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'New Menu Group')

            layoutGroupName = QHBoxLayout()
            lblGroupName = QLabel(self.tr('Group Name'))
            self.lnedtGroupName = QLineEdit('New Group', self)
            layoutGroupName.addWidget(lblGroupName)
            layoutGroupName.addWidget(self.lnedtGroupName)

            layoutGroupInfo = QHBoxLayout()
            lblGroupInfo = QLabel(self.tr('Group Info'))
            self.txtedtGroupInfo = QTextEdit(self)
            layoutGroupInfo.addWidget(lblGroupInfo)
            layoutGroupInfo.addWidget(self.txtedtGroupInfo)

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addLayout(layoutGroupName)
            layoutMine.addLayout(layoutGroupInfo)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec(self):
            ret = super().exec()
            # later - prevent lvng if lnedtGroupName blank
            return (
                ret, 
                self.lnedtGroupName.text()         if ret==self.DialogCode.Accepted else None,
                self.txtedtGroupInfo.toPlainText() if ret==self.DialogCode.Accepted else None,
                )
    
    class cEdtMnuDlgCopyMoveMenu(QDialog):
        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20
        
        def __init__(self, mnuGrp:int, menuID:int, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu')

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu {menuID}'))
            
            layoutMenuID = QHBoxLayout()
            lblMenuID = QLabel(self.tr('Menu ID'))
            self.combobxMenuID = QComboBox(self)
            definedMenus = menuItems.objects.filter(MenuGroup=mnuGrp, OptionNumber=0).values_list('MenuID', flat=True)
            self.combobxMenuID.addItems([str(n) for n in range(256) if n not in definedMenus])
            layoutMenuID.addWidget(lblMenuID)
            layoutMenuID.addWidget(self.combobxMenuID)
            
            visualgrpboxCopyMove = QGroupBox(self.tr("Copy / Move"))
            layoutgrpCopyMove = QHBoxLayout()
            # Create radio buttons
            radioCopy = QRadioButton(self.tr("Copy"))
            radioMove = QRadioButton(self.tr("Move"))
            # Add radio buttons to the layout
            layoutgrpCopyMove.addWidget(radioCopy)
            layoutgrpCopyMove.addWidget(radioMove)
            visualgrpboxCopyMove.setLayout(layoutgrpCopyMove)
            # Create a QButtonGroup for logical grouping
            self.lgclbtngrpCopyMove = QButtonGroup()
            self.lgclbtngrpCopyMove.addButton(radioCopy, id=self.intCMChoiceCopy)
            self.lgclbtngrpCopyMove.addButton(radioMove, id=self.intCMChoiceMove)
            # Add the QGroupBox to the main layout

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutMenuID)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                int(self.combobxMenuID.currentText()) if ret==self.DialogCode.Accepted else None,
                )
        ...
    
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        
        self.layoutmainMenu: QGridLayout = QGridLayout()
        self.WmenuItm: Dict[int, cEditMenu.wdgtmenuITEM] = {}
        self.layoutmenuHdr: QHBoxLayout = QHBoxLayout()
        self.layoutmenuHdrLeft: QVBoxLayout = QVBoxLayout()
        self.layoutmenuHdrRight: QVBoxLayout = QVBoxLayout()
        self._menuSOURCE = MenuRecords()
        self.currentMenu:QuerySet[menuItems] = None
        self.currRec:menuItems = None
        
        self.layoutmainMenu.setColumnStretch(0,1)
        self.layoutmainMenu.setColumnStretch(1,0)
        self.layoutmainMenu.setColumnStretch(2,1)
        # self.menuLayout.setColumnMinimumWidth(0,_SCRN_menuBTNWIDTH)
        # self.menuLayout.setColumnMinimumWidth(1,_SCRN_menuDIVWIDTH)
        # self.menuLayout.setColumnMinimumWidth(2,_SCRN_menuBTNWIDTH)
        
        self.layoutMenuHdrLn1 = QHBoxLayout()
        self.layoutMenuHdrLn2 = QHBoxLayout()

        self.lblmenuGroup:QLabel = QLabel(self.tr('Menu Group'), self)        
        self.lblmenuGroupName:QLabel = QLabel(self.tr('Group Name'), self)
        self.lblmenuID:QLabel = QLabel(self.tr('menu'), self)
        self.lblmenuName:QLabel = QLabel(self.tr('Menu Name'), self)
        self.lblnummenuGroupID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuID:  QLCDNumber = QLCDNumber(3)

        self.combxmenuGroup:QComboBox = cComboBoxFromDict(self.dictmenuGroup(), self)
        self.combxmenuGroup.setProperty('field', 'MenuGroup')
        self.combxmenuGroup.activated.connect(lambda: self.loadMenu(menuGroup=self.combxmenuGroup.currentData())) 
        self.lnedtmenuGroupName:QLineEdit = QLineEdit(self)
        self.lnedtmenuGroupName.setProperty('field', 'GroupName')
        self.lnedtmenuGroupName.editingFinished.connect(lambda: self.changeField(self.lnedtmenuGroupName))
        self.btnNewMenuGroup:QPushButton = QPushButton(self.tr('New Menu\nGroup'), self)
        self.btnNewMenuGroup.clicked.connect(self.createNewMenuGroup)
        self.combxmenuID:QComboBox = cComboBoxFromDict(self.dictmenus(), self)
        self.combxmenuID.setProperty('field', 'MenuID')
        self.combxmenuID.activated.connect(lambda: self.loadMenu(menuGroup=self.intmenuGroup, menuID=self.combxmenuID.currentData()))
        self.lnedtmenuName:QLineEdit = QLineEdit(self)
        self.lnedtmenuName.setProperty('field', 'OptionText')
        self.lnedtmenuName.editingFinished.connect(lambda: self.changeField(self.lnedtmenuName))
        
        self.btnRmvMenu:QPushButton = QPushButton(self.tr('Remove Menu'), self)
        self.btnRmvMenu.clicked.connect(self.rmvMenu)
        self.btnCopyMenu:QPushButton = QPushButton(self.tr('Copy/Move\nMenu'), self)
        self.btnCopyMenu.clicked.connect(self.copyMenu)
        
        self.layoutMenuHdrLn1.addWidget(self.lblmenuGroup)
        self.layoutMenuHdrLn1.addWidget(self.lblnummenuGroupID)
        self.layoutMenuHdrLn1.addWidget(self.combxmenuGroup)
        self.layoutMenuHdrLn1.addWidget(self.lblmenuGroupName)
        self.layoutMenuHdrLn1.addWidget(self.lnedtmenuGroupName)
        self.layoutMenuHdrLn1.addWidget(self.btnNewMenuGroup)
        
        self.layoutMenuHdrLn2.addWidget(self.lblmenuID)
        self.layoutMenuHdrLn2.addWidget(self.lblnummenuID)
        self.layoutMenuHdrLn2.addWidget(self.combxmenuID)
        self.layoutMenuHdrLn2.addWidget(self.lblmenuName)
        self.layoutMenuHdrLn2.addWidget(self.lnedtmenuName)
        self.layoutMenuHdrLn2.addWidget(self.btnRmvMenu)
        self.layoutMenuHdrLn2.addWidget(self.btnCopyMenu)
        
        self.btnCommit:QPushButton = QPushButton(self.tr('\nSave\nChanges\n'), self)
        self.btnCommit.clicked.connect(self.writeRecord)

        self.layoutmenuHdrLeft.addLayout(self.layoutMenuHdrLn1)
        self.layoutmenuHdrLeft.addLayout(self.layoutMenuHdrLn2)
        self.layoutmenuHdrRight.addWidget(self.btnCommit)
        self.layoutmenuHdrRight.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layoutmenuHdr.addLayout(self.layoutmenuHdrLeft)
        self.layoutmenuHdr.addLayout(self.layoutmenuHdrRight)
        
        self.layoutmainMenu.addLayout(self.layoutmenuHdr,0,0,1,3)
    ####
        self.bxFrame:List[QFrame] = [QFrame() for _ in range(_NUM_menuBUTTONS)]
        for bNum in range(_NUM_menuBUTTONS):
            self.bxFrame[bNum].setLineWidth(1)
            self.bxFrame[bNum].setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            self.layoutmainMenu.addWidget(self.bxFrame[bNum],y,x)
            
            self.WmenuItm[bNum] = None      # later - build WmenuItm before this loop?

        self.setWindowTitle(self.tr('Edit Menu'))
                    
        self.setLayout(self.layoutmainMenu)
        self.loadMenu()
    # __init__

    def dictmenuGroup(self) -> Dict[str, int]:
        # return Nochoice | { str(x): x.pk for x in menuGroups.objects.all() }    
        return { str(x): x.pk for x in menuGroups.objects.all() } 

    def dictmenus(self) -> Dict[str, int]:
        return { x.OptionText: x.MenuID for x in menuItems.objects.filter(MenuGroup=self.intmenuGroup, OptionNumber=0) } 


    ##########################################
    ########    Create

    def createNewMenuGroup(self):
        dlg = self.cEdtMnuDlgGetNewMenuGroupInfo(self)
        retval, grpName, grpInfo = dlg.exec()
        if retval:
            # new menuGroups record
            newrec = menuGroups(GroupName = grpName, GroupInfo = grpInfo)
            newrec.save()
            # create a default menu
            # newgroupnewmenu_menulist to menuItems
            for rec in newgroupnewmenu_menulist:
                menuItems.objects.create(MenuGroup = newrec, MenuID = 0, **rec)
            
            self.loadMenu(newrec.pk, 0)
        return
    
    def copyMenu(self):
        mnuGrp = self.intmenuGroup
        mnuID = self.intmenuID

        dlg = self.cEdtMnuDlgCopyMoveMenu(mnuGrp, mnuID, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec()
        if retval:
            qsFrom = self.currentMenu
            if CMChoiceCopy:
                qsdictTo = [
                    menuItems(**{**record.__dict__, "id": None, "MenuID": newMnuID})  # Set id to None to create new records
                    for record in qsFrom
                ]

                # Bulk insert the new records
                if qsdictTo:
                    with transaction.atomic():
                        menuItems.objects.bulk_create(qsdictTo)
            else:
                qsFrom.update(MenuID=newMnuID)
            #endif CMChoiceCopy
            self.loadMenu(mnuGrp, newMnuID)
        #endif retval

        return

        
    ##########################################
    ########    Read

    def displayMenu(self):
        menuGroup = self.intmenuGroup
        menuID = self.intmenuID
        menuItemRecs = self.currentMenu
        menuHdrRec:menuItems = menuItemRecs.get(OptionNumber=0)
        
        # set header elements
        self.lblnummenuGroupID.display(menuGroup)
        self.combxmenuGroup.setCurrentIndex(self.combxmenuGroup.findData(menuGroup))
        self.lnedtmenuGroupName.setText(menuHdrRec.MenuGroup.GroupName)
        self.lblnummenuID.display(menuID)
        self.combxmenuID.replaceDict(self.dictmenus())
        self.combxmenuID.setCurrentIndex(self.combxmenuID.findData(menuID))
        self.lnedtmenuName.setText(menuHdrRec.OptionText)

        for bNum in range(_NUM_menuBUTTONS):
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            bIndx = bNum+1
            mnuItmRc = menuItemRecs.filter(OptionNumber=bIndx).first()
            if not mnuItmRc:
                mnuItmRc = menuItems(
                    MenuGroup = menuGroups.objects.get(pk=menuGroup),
                    MenuID = menuID,
                    OptionNumber = bIndx,
                    )
            oldWdg = self.WmenuItm[bNum]
            if oldWdg:
                # remove old widget
                self.layoutmainMenu.removeWidget(oldWdg)
                oldWdg.hide()
                del oldWdg

            self.WmenuItm[bNum] = self.wdgtmenuITEM(mnuItmRc)
            self.layoutmainMenu.addWidget(self.WmenuItm[bNum],y,x) 
        # endfor
     
    # displayMenu

    def loadMenu(self, menuGroup: int = _DFLT_menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            menuGroup = SRC.dfltMenuGroup()
        if menuID==self._DFLT_menuID:
            menuID = SRC.dfltMenuID_forGroup(menuGroup)
    
        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDBRecs(menuGroup, menuID)
            self.currRec = self.currentMenu.get(OptionNumber=0)
            self.setFormDirty(self, False)       # should this be in displayMenu ?
            self.displayMenu()
        else:
            # menu doesn't exist; say so
            msg = QMessageBox(self)
            msg.setWindowTitle('Menu Doesn\'t Exist')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Menu {menuID} does\'t exist!')
            msg.open()
    # loadMenu


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
            'GroupName',
            }
        cRec:menuItems = self.currRec
        dbField = wdgt.property('field')

        wdgt_value = None

        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):
            kees = wdgt.selectedItem()['keys']
            wdgt_value = kees[0] if kees else wdgt.text()
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
        if dbField in valu_transform_flds:
            # wdgt_value = valu_transform_flds[dbField][1](wdgt_value)
            pass

        if wdgt_value or isinstance(wdgt_value,bool):
            if dbField != 'GroupName':  # GroupName belongs to cRec.MenuGroup; persist only at final write
                setattr(cRec, dbField, wdgt_value)
            self.setFormDirty(wdgt, True)
        
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    @Slot()
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:menuItems = self.currRec
        
        # check other traps later
        
        if self.isWdgtDirty(self.lnedtmenuGroupName):
            cRec.MenuGroup.GroupName = self.lnedtmenuGroupName.text()
            cRec.MenuGroup.save()

        cRec.save()
        
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    @Slot()
    def rmvMenu(self):
        
        pleaseWriteMe(self, 'Remove Menu')
        return
        
        (mGrp, mnu, mOpt) = (self.currRec.MenuGroup, self.currRec.MenuID, self.currRec.OptionNumber)
        
        # verify delete
        
        # remove from db
        if self.currRec.pk:
            self.currRec.delete()
        
        # replace with an "next" record
        self.currRec = menuItems(
            MenuGroup = mGrp,
            MenuID = mnu,
            OptionNumber = mOpt,
            )


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        if wdgt.property('noedit'):
            return
        
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')

    def isWdgtDirty(self, wdgt:QWidget) -> bool:
        return wdgt.property('dirty')


    ##########################################
    ########    Widget-responding procs
    

#############################################
#############################################

class _specialforms:
    EditMenu = '.-EDT-menu.-'
    # RunCode = ''
    RunSQLStatement = '.-ruN-sql.-'
    # ConstructSQLStatement = ''
    # LoadExtWebPage = ''
    # ChangePW = ''
    # EditParameters = ''
    # EditGreetings = ''
# FormNameToURL_Maps for internal use only
# FormNameToURL_Map['menu Argument'.lower()] = (url, view)
FormNameToURL_Map[_specialforms.EditMenu] = (None, cEditMenu)
FormNameToURL_Map[_specialforms.RunSQLStatement] = (None, cMRunSQL)

