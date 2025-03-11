from typing import (Dict, List, Tuple, Any, )

from django import db
from django.db import transaction
from django.db.models import QuerySet
from django.db.backends.utils import CursorWrapper

from PySide6.QtCore import (Qt, QObject,
    Signal, Slot, 
    QAbstractTableModel, QModelIndex, )
from PySide6.QtSql import (QSqlDatabase, QSqlTableModel, )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( QStyle, 
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, 
    QTableView, QHeaderView,
    QDialog, QMessageBox, QFileDialog, QDialogButtonBox,
    QLabel, QLCDNumber, QLineEdit, QTextEdit, QPlainTextEdit, QPushButton, QCheckBox, QComboBox, 
    QRadioButton, QGroupBox, QButtonGroup, 
    QSizePolicy, 
    )

# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 

from menuformname_viewMap import FormNameToURL_Map

from .dbmenulist import (MenuRecords, newgroupnewmenu_menulist, newmenu_menulist, )
from sysver import sysver
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .models import (menuItems, menuGroups, )
from .utils import (cComboBoxFromDict, cQFmFldWidg, cQFmNameLabel, QRawSQLTableModel, cQFmNameLabel,
    UnderConstruction_Dialog, areYouSure,
    Excelfile_fromqs, ExcelWorkbook_fileext,
    pleaseWriteMe, dictfetchall, 
    )

# copied from cMenu - if you change it here, change it there
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)

Nochoice = {'---': None}    # only needed for combo boxes, not datalists

# fontFormTitle = QFont()
# fontFormTitle.setFamilies([u"Copperplate Gothic"])
# fontFormTitle.setPointSize(24)


def FormBrowse(parntWind, formname, *args, **kwargs):
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
                theForm = fn(*args, **kwargs)
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
        
        self.lblFormName = cQFmNameLabel()
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
        self.lblHints = QPlainTextEdit()
        self.lblHints.setReadOnly(True)
        txtHints = 'PRAGMA table_list;'
        txtHints += '\nPRAGMA table_xinfo(tablname);'
        self.lblHints.setPlainText(txtHints)
        
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
        
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('SQL Results'))
        self.setWindowTitle(self.tr('SQL Results'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormSQLDescription = QFormLayout()
        lblOrigSQL = QLabel()
        lblOrigSQL.setText(origSQL)
        lblnRecs = QLabel()
        lblnRecs.setText(f'{len(rows)}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormSQLDescription.addRow('SQL Entered:', lblOrigSQL)
        self.layoutFormSQLDescription.addRow('rows affctd:', lblnRecs)
        self.layoutFormSQLDescription.addRow('cols:', lblcolNames)
        

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
        
        colfctr = 90
        self.setMinimumWidth(colfctr*len(colNames))
        
    @Slot()
    def DLResults(self):
        ExcelFileNamePrefix = "SQLresults"
        # Excel_qdict = [{self.colNames[x]:cRec[x] for x in range(len(self.colNames))} for cRec in self.rows]
        Excel_qdict = self.rows
        xlws = Excelfile_fromqs(Excel_qdict)
        filName, _ = QFileDialog.getSaveFileName(self, 
            caption="Enter Spreadsheet File Name",
            filter=f'{ExcelFileNamePrefix}*{ExcelWorkbook_fileext}',
            selectedFilter=f'*{ExcelWorkbook_fileext}'
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

#############################################
#############################################
#############################################

class cWidgetMenuItem(QWidget):

    requestMenuReload:Signal = Signal()
    
    class cEdtMnuItmDlg_CopyMove_MenuItm(QDialog):
        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20
        
        def __init__(self, menuGrp:int, menuID:int, optionNumber:int, parent:QWidget = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu Item')

            self.dlgButtons:QDialogButtonBox = None # to be defined later, but must exist now

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu Item {menuID}, {optionNumber}'))

            ##################################################
            # set up menuGroup, menuID, menuOption comboboxes
            layoutNewItemID = QGridLayout()

            lblMenuGroupID = QLabel(self.tr('Menu Group'))
            self.combobxMenuGroupID = cComboBoxFromDict(self.dictmenuGroup(), parent=self)
            self.combobxMenuGroupID.activated.connect(self.loadMenuIDs)

            lblMenuID = QLabel(self.tr('Menu'))
            self.combobxMenuID = cComboBoxFromDict(self.dictmenus(menuGrp), parent=self)
            # self.loadMenuIDs(menuGrp) - not necessary - done with initialization
            self.combobxMenuID.activated.connect(self.loadMenuOptions)

            lblMenuOption = QLabel(self.tr('Option'))
            self.combobxMenuOption = cComboBoxFromDict({}, parent=self)
            self.combobxMenuOption.activated.connect(self.menuOptionChosen)

            layoutNewItemID.addWidget(lblMenuGroupID,0,0)
            layoutNewItemID.addWidget(self.combobxMenuGroupID,1,0)
            layoutNewItemID.addWidget(lblMenuID,0,1)
            layoutNewItemID.addWidget(self.combobxMenuID,1,1)
            layoutNewItemID.addWidget(lblMenuOption,0,2)
            layoutNewItemID.addWidget(self.combobxMenuOption,1,2)

            self.combobxMenuGroupID.setCurrentIndex(self.combobxMenuGroupID.findData(menuGrp))
            self.loadMenuIDs(menuGrp)
            ##################################################            
            
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

            self.dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            self.dlgButtons.accepted.connect(self.accept)
            self.dlgButtons.rejected.connect(self.reject)            
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutNewItemID)
            layoutMine.addWidget(self.dlgButtons)
            
            self.setLayout(layoutMine)

        def dictmenuGroup(self) -> Dict[str, int]:
            return { str(x): x.pk for x in menuGroups.objects.all() } 
        def dictmenus(self, mnuGrp:int) -> Dict[str, int]:
            return Nochoice | { x.OptionText: x.MenuID for x in menuItems.objects.filter(MenuGroup=mnuGrp, OptionNumber=0) } 
        def dictmenuOptions(self, mnuID:int) -> List[int]:
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            definedOptions = menuItems.objects.filter(MenuGroup=mnuGrp, MenuID=mnuID).values_list('OptionNumber', flat=True)
            return Nochoice | { str(n+1): n+1 for n in range(_NUM_menuBUTTONS) if n+1 not in definedOptions }

        @Slot()
        def loadMenuIDs(self, idx:int):
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            # if self.combobxMenuGroupID.currentIndex() != -1:
            if mnuGrp is not None:
                self.combobxMenuID.replaceDict(self.dictmenus(mnuGrp))
            self.combobxMenuID.setCurrentIndex(-1)
            self.combobxMenuOption.clear()
            self.enableOKButton()
        @Slot()
        def loadMenuOptions(self, idx:int):
            mnuID:int = self.combobxMenuID.currentData()
            #if self.combobxMenuID.currentIndex() != -1:
            if mnuID is not None:
                self.combobxMenuOption.replaceDict(self.dictmenuOptions(mnuID))
            self.combobxMenuOption.setCurrentIndex(-1)
            self.enableOKButton()
        @Slot()
        def menuOptionChosen(self, idx:int):
            self.enableOKButton()
        def enableOKButton(self):
            if not self.dlgButtons:
                return
            all_GrpIdOption_chosen = all([
                self.combobxMenuGroupID.currentIndex() != -1,
                self.combobxMenuID.currentIndex() != -1,
                self.combobxMenuOption.currentIndex() != -1,
            ])
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(all_GrpIdOption_chosen)
        
        def exec(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            chosenMenuGroup = self.combobxMenuGroupID.currentData()
            chosenMenuID = self.combobxMenuID.currentData()
            chosenMenuOption = self.combobxMenuOption.currentData()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                # return (Group, Menu, OptrNum) tuple
                (chosenMenuGroup, chosenMenuID, chosenMenuOption),
                )
    
    def __init__(self, menuitmRec:menuItems, parent:QWidget = None):
        super().__init__(parent)
        
        self.setObjectName('cWidgetMenuItem')
        
        self.currRec = menuitmRec
        
        font = QFont()
        font.setPointSize(7)
        self.setFont(font)

        self.layoutFormMain = QHBoxLayout(self)
        self.layoutFormMain.setContentsMargins(0,0,0,0)
        self.layoutFormMain.setSpacing(0)
        
        self.layoutFormMainLeft = QVBoxLayout()
        self.layoutFormMainLeft.setContentsMargins(0,0,0,0)
        self.layoutFormMainLeft.setSpacing(0)

        ##
        self.layoutFormLine1 = QHBoxLayout()
        self.layoutFormLine1.setContentsMargins(0,0,0,0)
        self.layoutFormLine1.setSpacing(0)
        
        # self.lnedtOptionNumber = QLineEdit(self)
        self.lnedtOptionNumber = cQFmFldWidg(QLineEdit,
            lblText='Option Number', modlFld='OptionNumber', parent=self)
        # self.lnedtOptionNumber.setProperty('modelField', 'OptionNumber')
        # self.lnedtOptionNumber.setValue = self.lnedtOptionNumber.setText
        self.lnedtOptionNumber._wdgt.setProperty('noedit', True)
        self.lnedtOptionNumber._wdgt.setReadOnly(True)
        self.lnedtOptionNumber._wdgt.setFrame(False)
        self.lnedtOptionNumber._wdgt.setMaximumWidth(25)
        self.lnedtOptionNumber._wdgt.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.fldOptionText = cQFmFldWidg(QLineEdit, lblText='OptionText: ', modlFld='OptionText', parent=self)
        self.fldOptionText.signalFldChanged.connect(lambda: self.changeField(self.fldOptionText))

        self.fldMenuItemTopLine = cQFmFldWidg(QCheckBox, lblText='Top Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld='TopLine', parent=self)
        self.fldMenuItemTopLine.signalFldChanged.connect(lambda newstate: self.changeField(self.fldMenuItemTopLine))

        self.fldMenuItemBottomLine = cQFmFldWidg(QCheckBox, lblText='Btm Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld='BottomLine', parent=self)
        self.fldMenuItemBottomLine.signalFldChanged.connect(lambda newstate: self.changeField(self.fldMenuItemBottomLine))

        # self.layoutFormLine1.addWidget(self.lblOptionNumber)
        self.layoutFormLine1.addWidget(self.lnedtOptionNumber)
        self.layoutFormLine1.addWidget(self.fldOptionText)
        self.layoutFormLine1.addWidget(self.fldMenuItemTopLine)
        self.layoutFormLine1.addWidget(self.fldMenuItemBottomLine)

        ##

        self.layoutFormLine2 = QHBoxLayout()
        self.layoutFormLine2.setContentsMargins(0,0,0,0)
        self.layoutFormLine2.setSpacing(0)

        self.fldCommand = cQFmFldWidg(cComboBoxFromDict, lblText='Command:', modlFld='Command', 
            choices=vars(COMMANDNUMBER), parent=self)
        self.fldCommand.signalFldChanged.connect(lambda x: self.changeField(self.fldCommand))

        self.fldArgument = cQFmFldWidg(QLineEdit, lblText='Argument: ', modlFld='Argument', parent=self)
        self.fldArgument.signalFldChanged.connect(lambda: self.changeField(self.fldArgument))

        self.fldPWord = cQFmFldWidg(QLineEdit, lblText='Password: ', modlFld='PWord', parent=self)
        self.fldPWord.signalFldChanged.connect(lambda: self.changeField(self.fldPWord))

        self.layoutFormLine2.addWidget(self.fldCommand)
        self.layoutFormLine2.addWidget(self.fldArgument)
        self.layoutFormLine2.addWidget(self.fldPWord)

        self.layoutFormMainLeft.addLayout(self.layoutFormLine1)
        self.layoutFormMainLeft.addLayout(self.layoutFormLine2)
        ##
        
        self.layoutFormMainRight = QVBoxLayout()
        self.layoutFormMainRight.setContentsMargins(0,0,0,0)
        self.layoutFormMainRight.setSpacing(0)

        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(self.writeRecord)
        # self.btnCommit.setFixedSize(60, 30)  # Adjust width and height
        self.btnCommit.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnMoveCopy = QPushButton(self.tr('Copy / Move'), self)
        self.btnMoveCopy.clicked.connect(self.copyMenuOption)
        # self.btnMoveCopy.setFixedSize(60, 30)  # Adjust width and height
        self.btnMoveCopy.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnRemove = QPushButton(self.tr('Remove'), self)
        self.btnRemove.clicked.connect(self.rmvMenuOption)
        # self.btnRemove.setFixedSize(60, 30)  # Adjust width and height
        self.btnRemove.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.layoutFormMainRight.addWidget(self.btnMoveCopy)
        self.layoutFormMainRight.addWidget(self.btnRemove)
        self.layoutFormMainRight.addWidget(self.btnCommit)

        # # minimize sizing
        # for widget in [self.lnedtOptionNumber, self.fldOptionText, self.fldMenuItemTopLine, 
        #             self.fldMenuItemBottomLine, self.fldCommand, self.fldArgument, self.fldPWord, self.btnCommit]:
        #     widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # self.lnedtOptionNumber._wdgt.setFixedHeight(20)  # Adjust height to minimize space
        # self.fldOptionText._wdgt.setFixedHeight(20)
        # self.fldArgument._wdgt.setFixedHeight(20)
        # self.fldPWord._wdgt.setFixedHeight(20)

        self.layoutFormMain.addLayout(self.layoutFormMainLeft)
        self.layoutFormMain.addLayout(self.layoutFormMainRight)
        
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
                wdgtfld = getattr(wdgt, 'modelField', None)
                if callable(wdgtfld): wdgtfld = wdgtfld()
                if wdgtfld == field.name:
                    # set wdgt value to field_value
                    wdgt.setValue(field_valueStr)

                    break   # we found the widget for this field; we don't need to keep testing widgets
                # endif widget field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
        
        # fix this later ...
        
        self.btnMoveCopy.setEnabled(cRec.pk is not None)
        self.btnRemove.setEnabled(cRec.pk is not None)
        
        self.setFormDirty(self, False)
    # fillFormFromRec


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:cQFmFldWidg) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
        }
        cRec:menuItems = self.currRec
        dbField = wdgt.modelField()

        wdgt_value = None

        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        wdgt_value = wdgt.Value()

        if dbField in forgnKeys:
            dbField += '_id'
        if dbField in valu_transform_flds:
            wdgt_value = valu_transform_flds[dbField][1](wdgt_value)

        if wdgt_value or isinstance(wdgt_value,bool):
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
        
        cRec.save()
        pk = cRec.pk
                    
        self.btnMoveCopy.setEnabled(pk is not None)
        self.btnRemove.setEnabled(pk is not None)
        
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    def rmvMenuOption(self):
        # verify delete
        (mGrp, mnu, mOpt) = (self.currRec.MenuGroup, self.currRec.MenuID, self.currRec.OptionNumber)
        
        really = areYouSure(self, 
            title="Remove Menu Option?",
            areYouSureQuestion=f'Really remove menu option {mGrp}, {mnu}, {mOpt} ({self.currRec.OptionText}) ?'
            )
        
        if really != QMessageBox.StandardButton.Yes:
            return
        
        # remove from db
        if self.currRec.pk:
            self.currRec.delete()
            
        self.makeCurrecEmpty(mGrp, mnu, mOpt)
        
        self.requestMenuReload.emit()   # let listeners know we need a menu reload

    def makeCurrecEmpty(self, mGrp, mnu, mOpt):
        # replace with an empty record
        self.currRec = menuItems(
            MenuGroup_id = mGrp,
            MenuID = mnu,
            OptionNumber =mOpt,
            )


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:cQFmFldWidg, dirty:bool = True):
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
    
    def copyMenuOption(self):
        cRec = self.currRec
        mnuGrp = cRec.MenuGroup_id
        mnuID = cRec.MenuID
        optNum = cRec.OptionNumber

        dlg = self.cEdtMnuItmDlg_CopyMove_MenuItm(mnuGrp, mnuID, optNum, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec()
        if retval:
            newrec = menuItems.objects.get(pk=cRec.pk)
            newrec.pk = None
            newrec.MenuGroup_id = newMnuID[0]
            newrec.MenuID = newMnuID[1]
            newrec.OptionNumber = newMnuID[2]
            newrec.save()
            
            if CMChoiceCopy:
                ... # we've done everything we need to do
            else:
                if cRec.pk:
                    cRec.delete()
                self.makeCurrecEmpty(mnuGrp, mnuID, optNum)
            #endif CMChoiceCopy
            
            self.requestMenuReload.emit()   # let listeners know we need a menu reload
        # #endif retval

        return


class cEditMenu(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    

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
        
        self.layoutMenuHdrLn1 = QHBoxLayout()
        self.layoutMenuHdrLn2 = QHBoxLayout()

        self.fldmenuGroup:cQFmFldWidg = cQFmFldWidg(cComboBoxFromDict, lblText='Menu Group', modlFld='MenuGroup', 
            choices=self.dictmenuGroup(), parent= self)
        self.fldmenuGroup.signalFldChanged.connect(lambda idx: self.loadMenu(menuGroup=self.fldmenuGroup.Value())) 
        self.fldmenuGroupName:cQFmFldWidg = cQFmFldWidg(QLineEdit, lblText='Group Name', modlFld='GroupName', parent=self)
        self.fldmenuGroupName.signalFldChanged.connect(lambda: self.changeField(self.fldmenuGroupName))
        self.btnNewMenuGroup:QPushButton = QPushButton(self.tr('New Menu\nGroup'), self)
        self.btnNewMenuGroup.clicked.connect(self.createNewMenuGroup)
        self.fldmenuID:cQFmFldWidg = cQFmFldWidg(cComboBoxFromDict, lblText='menu', modlFld='MenuID', 
            choices=self.dictmenus(), parent=self)
        self.fldmenuID.signalFldChanged.connect(lambda idx: self.loadMenu(menuGroup=self.intmenuGroup, menuID=self.fldmenuID.Value()))
        self.fldmenuName:cQFmFldWidg = cQFmFldWidg(QLineEdit, lblText='Menu Name', modlFld='OptionText', parent=self)
        self.fldmenuName.signalFldChanged.connect(lambda: self.changeField(self.fldmenuName))
        
        self.lblnummenuGroupID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuGroupID.setMaximumSize(20,20)
        self.lblnummenuID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuID.setMaximumSize(20,20)

        self.btnRmvMenu:QPushButton = QPushButton(self.tr('Remove Menu'), self)
        self.btnRmvMenu.clicked.connect(self.rmvMenu)
        self.btnCopyMenu:QPushButton = QPushButton(self.tr('Copy/Move\nMenu'), self)
        self.btnCopyMenu.clicked.connect(self.copyMenu)
        
        self.layoutMenuHdrLn1.addWidget(self.fldmenuGroup)
        self.layoutMenuHdrLn1.addWidget(self.lblnummenuGroupID)
        self.layoutMenuHdrLn1.addWidget(self.fldmenuGroupName)
        self.layoutMenuHdrLn1.addWidget(self.btnNewMenuGroup)
        
        self.layoutMenuHdrLn2.addWidget(self.fldmenuID)
        self.layoutMenuHdrLn2.addWidget(self.lblnummenuID)
        self.layoutMenuHdrLn2.addWidget(self.fldmenuName)
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
        self.fldmenuGroup.setValue(menuGroup)
        self.fldmenuGroupName.setValue(menuHdrRec.MenuGroup.GroupName)
        self.lblnummenuID.display(menuID)
        self.fldmenuID.replaceDict(self.dictmenus())
        self.fldmenuID.setValue(menuID)
        self.fldmenuName.setValue(menuHdrRec.OptionText)

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
            self.WmenuItm[bNum].requestMenuReload.connect(lambda: self.loadMenu(self.intmenuGroup, self.intmenuID))
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
    def changeField(self, wdgt:cQFmFldWidg) -> bool:
        # move to class var?
        forgnKeys = {   
            'MenuGroup',
            }
        # move to class var?
        valu_transform_flds = {
            'GroupName',
            }
        cRec:menuItems = self.currRec
        dbField = wdgt.modelField()

        wdgt_value = wdgt.Value()

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
        
        if self.isWdgtDirty(self.fldmenuGroupName):
            cRec.MenuGroup.GroupName = self.fldmenuGroupName.Value()
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
# class EditMenu


#############################################
#############################################
#############################################


class cQSQLTableModel_NEW(QSqlTableModel):
    # def __init__(self, rows:List[Dict[str,Any]], colNames:List[str], parent:QObject = None):
    def __init__(self, tblName:str, db:QSqlDatabase = QSqlDatabase.database(), parent:QObject = None):
        super().__init__(parent, db)
        self.setTable(tblName)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)    # think about this - pass as parm?
        self.select()
    
    # def rowCount(self, parent = QModelIndex()):
    #     return len(self.queryset)
    
    # def columnCount(self, parent = QModelIndex()):
    #     return len(self.headers)
    
    # def data(self, index, role = Qt.DisplayRole):
    #     if not index.isValid():
    #         return None
    #     if role == Qt.ItemDataRole.DisplayRole:
    #         rec = self.queryset[index.row()]
    #         fldName = self.headers[index.column()]
    #         value = rec[fldName]

    #         return value
    #     # endif role
    #     return None

    # # not editable - don't need setData

    # def headerData(self, section, orientation, role = Qt.DisplayRole):
    #     if role == Qt.DisplayRole:
    #         if orientation == Qt.Orientation.Horizontal:
    #             return self.headers[section]
    #         elif orientation == Qt.Orientation.Vertical:
    #             return str(section+1)
    #         #endif orientation
    #     # endif role
    #     return None


#############################################
#############################################
#############################################

from incShip.database import incShipDatabase
class OpenTable(QWidget):
    _tableListSQL:str = 'PRAGMA table_list;'
    
    def __init__(self, tbl:str = None, parent:QWidget = None):
        super().__init__(parent)
        
        # font = QFont()
        # font.setPointSize(12)
        # self.setFont(font)
        
        db = incShipDatabase
        if not tbl:
            # get tbl name
                # use self._tableListSQL
            # read all table names
            # present and select
            ...
        
        # for testing ...
        tbl = 'incShip_hbl'
        
        # read into model
        # verify tbl exists
        # error, rows, colNames = self.getTable(tbl)
        error, rows, colNames = (None, [], [])
        if error:
            raise error
        
        # tblWidget = self.tableWidget(rows, colNames)
        tblWidget = self.tableWidget(tbl, db)
        # bring all rows in so rowCount will be correct
        while tblWidget.model().canFetchMore():
            tblWidget.model().fetchMore()
        rows = tblWidget.model().rowCount()
        colNames = [tblWidget.model().headerData(n, Qt.Orientation.Horizontal) for n in range(tblWidget.model().columnCount())]
        # present TableView

        # save incoming for future use if needed
        self.rows = rows
        self.colNames = colNames

        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Table'))
        self.setWindowTitle(self.tr('Table'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormTableDescription = QFormLayout()
        lblnRecs = QLabel()
        lblnRecs.setText(f'{rows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormTableDescription.addRow('rows:', lblnRecs)
        self.layoutFormTableDescription.addRow('cols:', lblcolNames)

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        self.layoutFormMain.addWidget(tblWidget)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormTableDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        
    def getTable(self, tblName:str) -> Tuple[Exception|None, List[Dict[str, Any]], List[str]|str]:
        inputSQL:str = f'SELECT * FROM {tblName}'
        # inputSQL:str = f'SELECT * FROM %(tblName)s'
        sqlerr = None
        with db.connection.cursor() as djngocursor:
            try:
                djngocursor.execute(inputSQL)
                # djngocursor.execute(inputSQL, [tblName])
            except Exception as err:
                sqlerr = err
            colNames = []
            rows = []
            if not sqlerr:
                if djngocursor.description:
                    colNames = [col[0] for col in djngocursor.description]
                    rows = dictfetchall(djngocursor)
                else:
                    colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
                    rows = []
                #endif cursor.description
            else:  
                # nothing to do
                ...
            #endif not sqlerr
        #end with
        
        return (sqlerr, rows, colNames)

    # def tableWidget(self, rows:List[Dict[str, Any]], colNames:str|List[str]) -> QTableView:
    def tableWidget(self, tbl, db) -> QTableView:
        resultModel = cQSQLTableModel_NEW(tbl, db, self.parent())
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
        
        return resultTable
        

#############################################
#############################################
#############################################


class _internalForms:
    EditMenu = '.-EDT-menu.-'
    OpenTable = '-.OPN-tbL.-'
    # RunCode = ''
    RunSQLStatement = '.-ruN-sql.-'
    # ConstructSQLStatement = ''
    # LoadExtWebPage = ''
    # ChangePW = ''
    # EditParameters = ''
    # EditGreetings = ''
# FormNameToURL_Maps for internal use only
# FormNameToURL_Map['menu Argument'.lower()] = (url, view)
FormNameToURL_Map[_internalForms.EditMenu] = (None, cEditMenu)
FormNameToURL_Map[_internalForms.OpenTable] = (None, OpenTable)
FormNameToURL_Map[_internalForms.RunSQLStatement] = (None, cMRunSQL)

