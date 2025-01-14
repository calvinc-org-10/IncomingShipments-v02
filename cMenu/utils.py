from typing import (Dict, List, Any, )
from collections.abc import (Callable, )

from PySide6.QtCore import (QCoreApplication,
    Qt, Slot, QObject,
    QRect,
    QStringListModel, QAbstractTableModel, QAbstractListModel, QModelIndex,
    )
# from PySide6.QtGui import (
#    )
from PySide6.QtWidgets import (QApplication, QWidget,
    QVBoxLayout, QScrollArea, QFrame, QGridLayout,
    QLineEdit, QCompleter, 
    QComboBox, QPushButton,
    )



class cDataList(QLineEdit):
    """
    A LineEdit box that acts like an HTML DataList
    Choice matches are choices which contain the input string, case-insensitive
    
    caller should connect the editingFinished signal to a slot which is aware of the cDataList
        and is in scope to call cDataList.selectedItem
    ex: self.testdatalist.editingFinished.connect(self.showHBLChosen)

    Args:
        choices:Dict[Any, str], {key: 'value to display/lookup'}
        initval:str = '', (not currently implemented)
        parent:QWidget=None

    def selectedItem(self):
        returns the following dictionary: 
        return {'keys': [key for key, t in self.choices.items() if t==self.text()], 'text': self.text()}
        (all keys matching the text input)
    """
    def __init__(self, choices:Dict[Any, str], initval:str = '', parent:QWidget=None):
        super().__init__(initval, parent)

        self.choices = choices
        
        self.setClearButtonEnabled(True)
        
        choices_to_present = list(choices.values())
        qCompleterObj = QCompleter(QStringListModel(choices_to_present, self), self)
        qCompleterObj.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        qCompleterObj.setFilterMode(Qt.MatchFlag.MatchContains)
        qCompleterObj.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        self.setCompleter(qCompleterObj)
    # __ init__
    
    def selectedItem(self):
        """
        def selectedItem(self):
            returns the following dictionary: 
            return {'keys': [key for key, t in self.choices.items() if t==self.text()], 'text': self.text()}
            (all keys matching the text input)
        """
        return {'keys': [key for key, t in self.choices.items() if t==self.text()], 'text': self.text()}
    # selectedItem
    
    def addChoices(self, choices:Dict[Any, str]):
        self.choices.update(choices)
        
        choices_to_present = list(self.choices.values())
        newmodel = QStringListModel(choices_to_present, self)
        self.completer().setModel(newmodel)
    # addChoices




from PySide6.QtCore import QAbstractTableModel, Qt

class cDictModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        """
        Initialize the model with a dictionary.
        
        Args:
            data (dict): Dictionary to model.
        """
        super().__init__(parent)
        self._data = data
        self._keys = list(data.keys())

    def rowCount(self, parent=None):
        """Return the number of rows in the model."""
        return len(self._data)

    def columnCount(self, parent=None):
        """Return the number of columns in the model (Key and Value)."""
        return 2  # One for the key and one for the value

    def data(self, index, role=Qt.DisplayRole):
        """Return the data for a given cell."""
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = index.row()
        col = index.column()

        key = self._keys[row]
        if col == 0:  # Key column
            return key
        elif col == 1:  # Value column
            return self._data[key]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return the header labels for rows or columns."""
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return ["Key", "Value"][section]  # Column headers
        elif orientation == Qt.Vertical:
            return str(section + 1)  # Row numbers
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Set the data for a given cell."""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()
        key = self._keys[row]

        if col == 1:  # Only allow editing the value column
            self._data[key] = value
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def flags(self, index):
        """Set flags for each cell."""
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:  # Only value column is editable
            flags |= Qt.ItemIsEditable

        return flags

class cComboBoxFromDict(QComboBox):
    """
    Generates QComboBox from dictionary

    Args:
        dict (Dict): The input dictionary. The values will be the data returned by currentData, and
            the keys will be the values shown in the QComboBox
        parent (QWidget) default None
    
    """
    _combolist:List = []
    
    def __init__(self, dict:Dict, parent:QWidget = None):
        super().__init__(parent)
        
        # don't do completers - assume underlying QComboBox is non-editable
        # choices_to_present = list(dict)
        # qCompleterObj = QCompleter(QStringListModel(choices_to_present, self), self)
        # qCompleterObj.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # qCompleterObj.setFilterMode(Qt.MatchFlag.MatchContains)
        # qCompleterObj.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        # self.setCompleter(qCompleterObj)

        for key, val in dict.items():
            self.addItem(key,val)
            self._combolist.append({key:val})

#########################################        
#########################################        

# cQRecordsetView - Scrollable layout of records
class cQRecordsetView(QWidget):
    _newdgt_fn:Callable[[], QWidget] = None
    _btnAdd:QPushButton = None
    def __init__(self, newwidget_fn:Callable[[], QWidget] = None, parent=None):
        """
        Widget which displays a set of records

        Args:
            newwidget_fn (Callable, optional): . Defaults to None. newwidget_fn() should return a new record 
                in a widget suitable for adding to this layout
            parent (_type_, optional): _description_. Defaults to None.
        """
        super().__init__(parent)
        self._newdgt_fn = newwidget_fn
        self.init_ui()

    def init_ui(self):
        self.mainLayout = QVBoxLayout(self)

        # set up scroll area
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mainLayout.addWidget(self.scrollarea)
    
        # Container widget for the layout
        self.scrollwidget = QWidget()
        # layout for the scrollwidget
        self.scrolllayout = QVBoxLayout(self.scrollwidget)
        # # Set container as the scroll area widget
        self.scrollarea.setWidget(self.scrollwidget)

        if self._newdgt_fn:
            self._btnAdd = QPushButton(self.scrollwidget)
            self._btnAdd.setObjectName('AddBtnQRS')
            self._btnAdd.setText('\nAdd\n')
            self._btnAdd.clicked.connect(self.addBtnClicked)
            self.scrolllayout.addWidget(self._btnAdd)

        self.init_recSet()
    # init_ui

    def setAddText(self, addText:str = '\nAdd\n'):
        ...
    # setAddText

    def addWidget(self, wdgt:QWidget):
        insAt = self.scrolllayout.count()-1 if self._newdgt_fn else -1
        self.scrolllayout.insertWidget(insAt, wdgt)
        line = QFrame(self)
        myWidth = self.geometry().width()
        line.setGeometry(QRect(0, 0, myWidth, 3))
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.scrolllayout.insertWidget(insAt+1, line)
    # addWidget

    # addLayout needed?

    def init_recSet(self):
        # remove all widgets from scrolllayout
        # for wdgt in self.scrolllayout:
        idx = 0
        child = self.scrolllayout.itemAt(idx)
        while child != None:
            if child.widget() == self._btnAdd:   # don't removew the Add Button!
                idx += 1
            else:
                widg = self.scrolllayout.takeAt(idx)
                widg.widget().deleteLater() # del the widget
            # endif child == self._btnAdd
            child = self.scrolllayout.itemAt(idx)
    # init_recSet
    
    @Slot()
    def addBtnClicked(self):
        if callable(self._newdgt_fn):
            self.addWidget(self._newdgt_fn())
    # addBtnClicked


#########################################        
#########################################        

class NOPETHATSNOTIT(QAbstractListModel):
    def __init__(self, data:Dict[str,Any], parent:QObject=None):
        """
        Initialize the model with a list of dictionaries.
        
        Args:
            data (list of dict): List of dictionaries to model.
        """
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None) -> int:
        """Return the number of rows in the model."""
        return len(self._data)

    # def columnCount(self, parent=None) -> int:
    #     """Return the number of columns in the model."""
    #     return len(self._headers)

    def data(self, index:QModelIndex, role:Qt.ItemDataRole=Qt.DisplayRole) -> Any|None:
        """Return the data for a given cell."""
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = index.row()
        col = index.column()
        key = self._headers[col]
        return self._data[row].get(key, None)

    def headerData(self, section:int, orientation:Qt.Orientation, role:Qt.ItemDataRole=Qt.DisplayRole) -> str|int|None:
        """Return the header labels for rows or columns."""
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]  # Column headers (dictionary keys)
        elif orientation == Qt.Vertical:
            return str(section + 1)  # Row numbers
        return None

    def setData(self, index:QModelIndex, value:Any, role:Qt.ItemDataRole=Qt.EditRole) -> bool:
        """Set the data for a given cell."""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()
        key = self._headers[col]
        self._data[row][key] = value
        self.dataChanged.emit(index, index, [role])
        return True

    def flags(self, index:QModelIndex) -> Qt.ItemFlag:
        """Set flags for each cell."""
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

