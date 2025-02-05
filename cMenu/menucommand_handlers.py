from typing import (Dict, List, )

from django import db
from django.db.backends.utils import CursorWrapper

from PySide6.QtCore import (Qt, QObject, QAbstractTableModel, QModelIndex, )
from PySide6.QtGui import (QFont, )
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame, 
    QTableView, QHeaderView,
    QDialog, QMessageBox, 
    QTextEdit, QPushButton, QDialogButtonBox, QLabel, 
    QSizePolicy, 
    )

from kls_cMenu import cMenu
from utils import Excelfile_fromqs, dictfetchall

fontFormTitle = QFont()
fontFormTitle.setFamilies([u"Copperplate Gothic"])
fontFormTitle.setPointSize(24)


def EditMenu_init():
    ...

def MenuCreate():
    ...

def MenuRemove():
    ...

class cMRunSQL(QWidget):
    wndwGetSQL:QWidget = None
    wndwShowSQL:QWidget = None
    inputSQL:str = ''
    cntext:Dict = {}    # holdover from django client-server apps

    class QWGetSQL(QWidget):
        def __init__(self, parent = None):
            super().__init__(parent)

            # self.resize(std_windowsize.width(), std_windowsize.height()+150) # this is a temporary fix
            font = QFont()
            font.setPointSize(12)
            self.setFont(font)
            
            self.layoutForm = QVBoxLayout(self)
            
            thisWindowsize = self.size()

            # self.layoutwidgetFormHdr = QWidget()
            self.layoutFormHdr = QVBoxLayout()
            
            self.lblFormName = QLabel(self)
            wdgt = self.lblFormName
            wdgt.setFont(fontFormTitle)
            wdgt.setFrameShape(QFrame.Shape.Panel)
            wdgt.setFrameShadow(QFrame.Shadow.Raised)
            wdgt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wdgt.setWordWrap(True)
            wdgt.setText(self.tr('Enter SQL'))
            self.layoutFormHdr.addWidget(wdgt,0,0)
            self.layoutFormHdr.addSpacing(20)
            self.layoutForm.addLayout(self.layoutFormHdr)
            
            # main area for entering SQL
            
            # run/Cancel buttons
            
            # Hints
            
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
        # present wndwGetSQL
        
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

