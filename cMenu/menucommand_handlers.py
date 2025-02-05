from typing import (Dict, List, )

from django import db
from django.db.backends.utils import CursorWrapper

from PySide6.QtCore import (Qt, QObject, QAbstractTableModel, QModelIndex, )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( QStyle, 
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, 
    QTableView, QHeaderView,
    QDialog, QMessageBox, 
    QTextEdit, QPushButton, QDialogButtonBox, QLabel, 
    QSizePolicy, 
    )

# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 
from .utils import Excelfile_fromqs, dictfetchall, pleaseWriteMe

fontFormTitle = QFont()
fontFormTitle.setFamilies([u"Copperplate Gothic"])
fontFormTitle.setPointSize(24)


def EditMenu_init():
    ...

def MenuCreate():
    ...

def MenuRemove():
    ...

class QWGetSQL(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        # self.resize(std_windowsize.width(), std_windowsize.height()+150) # this is a temporary fix
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # self.layoutwidgetFormHdr = QWidget()
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = QLabel()
        self.lblFormName.setFont(fontFormTitle)
        self.lblFormName.setFrameShape(QFrame.Shape.Panel)
        self.lblFormName.setFrameShadow(QFrame.Shadow.Raised)
        self.lblFormName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblFormName.setWordWrap(True)
        self.lblFormName.setText(self.tr('Enter SQL'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)
        
        # main area for entering SQL
        self.layoutFormMain = QFormLayout()
        self.txtedSQL = QTextEdit()
        self.layoutFormMain.addRow(self.tr('SQL statement'), self.txtedSQL)
        
        # run/Cancel buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonRunSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.Computer), self.tr('Run SQL') ) 
        self.buttonRunSQL.clicked.connect(lambda: pleaseWriteMe(self,'buttonRunSQL.clicked.connect') )
        self.layoutFormActionButtons.addWidget(self.buttonRunSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme('dialog-cancel'), self.tr('Cancel') ) 
        self.buttonCancel.clicked.connect(lambda: pleaseWriteMe(self,'buttonCancel.clicked.connect'))
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
        
    
#class cMRunSQL_THE_REAL_ONE(QWidget):
class cMRunSQL(QWidget):
    # wndwGetSQL:QWidget = None
    # wndwShowSQL:QWidget = None

    class QRawSQLTableModel(QAbstractTableModel):
        def __init__(self, cursor:CursorWrapper, colNames:List[str], parent:QObject = None):
            super().__init__(parent)
            self.headers = colNames
            self.queryset = dictfetchall(cursor)
        
        def rowCount(self, parent = QModelIndex()):
            return len(self.queryset)
        
        def columnCount(self, parent = QModelIndex()):
            return len(self.headers)
        
        def data(self, index, role = Qt.DisplayRole):
            if not index.isValid():
                return None
            if role == Qt.ItemDataRole.DisplayRole:
                rec = self.queryset[index.row()]
                fldName = self.headers[index.column()]
                value = rec[fldName]

                return value
            # endif role
            return None

        # not editable - don't need setData
    
        def headerData(self, section, orientation, role = Qt.DisplayRole):
            if role == Qt.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self.headers[section]
                elif orientation == Qt.Orientation.Vertical:
                    return str(section+1)
                #endif orientation
            # endif role
            return None

    
    def __init__(self, parent = None):
        super().__init__(parent)
        
        # create windows
        self.wndwGetSQL = QWGetSQL(parent)
        self.wndwGetSQL.setAttribute(Qt.WA_DeleteOnClose)

        # they get shown at self.show()

    def show(self):
        self.wndwGetSQL.show()
        
    def fn_cRawSQL_exec(self):
        cntext = []
        ...
        # build form -> inputSQL
        sqlerr = None
        with db.connection.cursor() as cursor:
            try:
                cursor.execute(self.inputSQL)
            except Exception as err:
                sqlerr = err
        if not sqlerr:
            colNames = []
            if cursor.description:
                colNames = [col[0] for col in cursor.description]
                #rows = dictfetchall(cursor)
                cntext['colNames'] = colNames
                cntext['nRecs'] = cursor.rowcount
                cntext['SQLresults'] = cursor

            else:
                cntext['colNames'] = 'NO RECORDS RETURNED; ' + str(cursor.rowcount) + ' records affected'
                cntext['nRecs'] = cursor.rowcount
                cntext['SQLresults'] = cursor

            self.fn_cRawSQL_show(cursor, colNames)
        else:  
            # show sqlerr in self.wndwGetSQL
            ...
        #endif not sqlerr

    def fn_cRawSQL_show(self, cursor, colNames):
        # close         self.wndwGetSQL
        # present results in QTableView
        resultModel = self.QRawSQLTableModel(cursor, colNames, self)
        self.tblViewInvoices.setModel(resultModel)

        resultTable = QTableView(self)
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

        ExcelFileNamePrefix = "SQLresults "
        Excel_qdict = [{colNames[x]:cRec[x] for x in range(len(colNames))} for cRec in cursor]
        Excelfile_fromqs(Excel_qdict)
        
        ...

