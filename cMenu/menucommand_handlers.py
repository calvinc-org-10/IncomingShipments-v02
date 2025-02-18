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
    QDialog, QMessageBox, QFileDialog, 
    QTextEdit, QPushButton,  QLabel, 
    QSizePolicy, 
    )

# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 

from menuformname_viewMap import FormNameToURL_Map

from .utils import (Excelfile_fromqs, ExcelWorkbook_fileext, dictfetchall, QRawSQLTableModel, UnderConstruction_Dialog )


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
    formname = formname.lower()
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


