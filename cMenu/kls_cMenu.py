from typing import Dict, List

from PySide6.QtCore import (QCoreApplication, 
    QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,
    Signal, Slot, )
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QDialog, QMessageBox, 
    QPushButton, QDialogButtonBox, QLabel, QFrame, QLineEdit, QCheckBox,
    QSizePolicy, 
    )
from PySide6.QtSvgWidgets import QSvgWidget

from django.db.models import QuerySet

from .dbmenulist import MenuRecords
from sysver import sysver
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from . import menucommand_handlers
from .models import (menuItems, menuGroups, )
from .utils import (cComboBoxFromDict, pleaseWriteMe, )

# TODO: put in class?
# cMenu-related constants
_SCRN_menuBTNWIDTH:int = 100
_SCRN_menuDIVWIDTH:int = 20
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)

#############################################
#############################################
#############################################

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
        self.lnedtOptionNumber.setReadOnly(True)
        self.lnedtOptionNumber.setFrame(False)
        self.lnedtOptionNumber.setMaximumWidth(40)
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
        self.lnedtBottomLine.setReadOnly(True)
        self.lnedtBottomLine.setFrame(False)
        self.lnedtBottomLine.setMaximumWidth(40)
        self.lnedtBottomLine.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.layoutBottomLine.addWidget(self.lnedtBottomLine)
        self.layoutBottomLine.addWidget(self.chkbxBottomLine)

        self.layoutFormLine1.addWidget(self.lblOptionNumber)
        self.layoutFormLine1.addWidget(self.lnedtOptionNumber)
        self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addWidget(self.lblOptionText)
        self.layoutFormLine1.addWidget(self.lnedtOptionText)
        self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addLayout(self.layoutTopLine)
        self.layoutFormLine1.addLayout(self.layoutBottomLine)

        ##

        self.layoutFormLine2 = QHBoxLayout()

        self.lblCommand = QLabel(self)
        self.lblCommand.setText(self.tr('Command: '))
        self.cmbobxCommand = cComboBoxFromDict(COMMANDNUMBER, self)
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
        self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.lblArgument)
        self.layoutFormLine2.addWidget(self.lnedtArgument)
        self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.lblPWord)
        self.layoutFormLine2.addWidget(self.lnedtPWord)

        ##
        
        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(lambda: pleaseWriteMe(self, 'save Menu Irtem changes'))
        self.layoutFormLine2.addSpacing(5)
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
    
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:menuItems = self.currRec
        newrec = (cRec is None)
        
        # check other traps later
        
        cRec.save()
        pk = cRec.pk
        
        if newrec:
            # add this record to self.gotoHBL.completer().model()
            ...
            
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    # Delete not supported yet


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
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')


    ##########################################
    ########    Widget-responding procs

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
            
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)
        
        self.menuLayout: QGridLayout = QGridLayout()
        self.WmenuItm: Dict[int, cEditMenu.wdgtmenuITEM] = {}
        self.menuHdrLayout: QHBoxLayout = QHBoxLayout()
        self.lblmenuID: QLabel = QLabel("")
        self.lblmenuName: QLabel = QLabel("")
        self._menuSOURCE = MenuRecords()
        self.currentMenu: QuerySet = None
        
        self.menuLayout.setColumnStretch(0,1)
        self.menuLayout.setColumnStretch(1,0)
        self.menuLayout.setColumnStretch(2,1)
        
        self.setLayout(self.menuLayout)
        
        self.menuHdrLayout.addWidget(self.lblmenuID, stretch=0, alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.menuHdrLayout.addWidget(self.lblmenuName, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.menuLayout.addLayout(self.menuHdrLayout,0,0,1,3)
        
        self.lblmenuID.setFont(QFont("Arial",8))
        self.lblmenuID.setMargin(10)
        self.lblmenuName.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.lblmenuName.setFont(QFont("Century Gothic", 24))
        # self.menuName.setMargin(20)
        self.lblmenuName.setWordWrap(False)

        self.bxFrame:List[QFrame] = [QFrame() for _ in range(_NUM_menuBUTTONS)]
        for bNum in range(_NUM_menuBUTTONS):
            self.bxFrame[bNum].setLineWidth(1)
            self.bxFrame[bNum].setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
            
        self.setWindowTitle(self.tr('Edit Menu'))
                    
        self.loadMenu()
    # __init__

    def clearoutMenu(self):
        self.lblmenuID.setText("")
        self.lblmenuName.setText("")
        for bNum in range(_NUM_menuBTNperCOL):
            self.WmenuItm[bNum].setText("\n\n")
            self.WmenuItm[bNum].setEnabled(False)
            self.WmenuItm[bNum+_NUM_menuBTNperCOL].setText("\n\n")
            self.WmenuItm[bNum+_NUM_menuBTNperCOL].setEnabled(False)
    
    def displayMenu(self):
        menuGroup = self.intmenuGroup
        menuID = self.intmenuID
        menuItemRecs = self.currentMenu
        
        self.lblmenuID.setText(f'{menuGroup},{menuID}\n{sysver["DEV"]}')
        self.lblmenuName.setText(str(menuItemRecs[0].OptionText))

        for bNum in range(_NUM_menuBTNperCOL):
            # column 1
            bIndx = bNum+1
            mnuItmRc = menuItemRecs.filter(OptionNumber=bIndx).first()
            if not mnuItmRc:
                mnuItmRc = menuItems(
                    MenuGroup = menuGroups.objects.get(pk=menuGroup),
                    MenuID = menuID,
                    OptionNumber = bIndx,
                    )
            self.WmenuItm[bNum] = self.wdgtmenuITEM(mnuItmRc)
            
            oldWdg = self.menuLayout.itemAtPosition(bNum+1,0)
            if oldWdg:
                self.menuLayout.removeItem(oldWdg)
                del oldWdg
                
            self.menuLayout.addWidget(self.bxFrame[bNum],bNum+1,0)
            self.menuLayout.addWidget(self.WmenuItm[bNum],bNum+1,0) # must add widget last so it become editable
            
            # column 2
            bIndx = bNum+1+_NUM_menuBTNperCOL
            mnuItmRc = menuItemRecs.filter(OptionNumber=bIndx).first()
            if not mnuItmRc:
                mnuItmRc = menuItems(
                    MenuGroup = menuGroups.objects.get(pk=menuGroup),
                    MenuID = menuID,
                    OptionNumber = bIndx,
                    )
            self.WmenuItm[bNum+_NUM_menuBTNperCOL] = self.wdgtmenuITEM(mnuItmRc, self.parent())
            
            oldWdg = self.menuLayout.itemAtPosition(bNum+1,2)
            if oldWdg:
                self.menuLayout.removeItem(oldWdg)
                del oldWdg
            self.menuLayout.addWidget(self.bxFrame[bNum+_NUM_menuBTNperCOL],bNum+1,2)
            self.menuLayout.addWidget(self.WmenuItm[bNum+_NUM_menuBTNperCOL],bNum+1,2) # must add widget last so it become editable
        # endfor
     
    def loadMenu(self, menuGroup: int = _DFLT_menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            menuGroup = SRC.dfltMenuGroup()
            pass
        if menuID==self._DFLT_menuID:
            menuID = SRC.dfltMenuID_forGroup(menuGroup)
    
        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDBRecs(menuGroup, menuID)
            self.displayMenu()
        else:
            # menu doesn't exist; say so
            msg = QMessageBox(self)
            msg.setWindowTitle('Menu Doesn\'t Exist')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Menu {menuID} does\'t exist!')
            msg.open()
    

#############################################
#############################################

class cMenu(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    menuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    
    # don't try to do this here - QWidgets cannot be created before QApplication
    # menuScreen: QWidget = QWidget()
    # menuLayout: QGridLayout = QGridLayout()
    # menuButton: Dict[int, QPushButton] = {}
    class menuBUTTON(QPushButton):
        btnNumber:int = 0
        def __init__(self, btnNumber:int):
            super().__init__()
            self.btnNumber = btnNumber
            self.setText("\n\n")
            self.setObjectName(f'cMenuBTN-{btnNumber}')
            
    def __init__(self, parent:QWidget, initMenu=(0,0), mWidth=None, mHeight=None):
        super().__init__(parent)
        
        self.menuScreen: QWidget = QWidget(parent)
        self.menuLayout: QGridLayout = QGridLayout()
        self.menuButton: Dict[int, cMenu.menuBUTTON] = {}
        self.menuHdrLayout: QHBoxLayout = QHBoxLayout()
        self.lblmenuID: QLabel = QLabel("")
        self.lblmenuName: QLabel = QLabel("")
        self._menuSOURCE = MenuRecords()
        self.currentMenu: Dict[int,Dict] = {}
        
        self.childScreens: Dict[str,QWidget] = {}

        self.menuLayout.setColumnStretch(0,1)
        self.menuLayout.setColumnStretch(1,0)
        self.menuLayout.setColumnStretch(2,1)
        self.menuLayout.setColumnMinimumWidth(0,_SCRN_menuBTNWIDTH)
        self.menuLayout.setColumnMinimumWidth(1,_SCRN_menuDIVWIDTH)
        self.menuLayout.setColumnMinimumWidth(2,_SCRN_menuBTNWIDTH)
        
        self.menuLayout.setRowMinimumHeight(1,10)
        
        if not self.menuScreen.objectName():
            self.menuScreen.setObjectName("cMenu")
        mWidth = mWidth if mWidth else parent.width()
        mHeight = mHeight if mHeight else parent.height()
        self.menuScreen.resize(mWidth, mHeight)
        
        self.menuScreen.setLayout(self.menuLayout)
        
        _menu_BTNWIDTH_min = int((mWidth-20)/5)
        _menu_BTNWIDTH_max = int((mWidth-20)/2.5)
        
        self.menuHdrLayout.addWidget(self.lblmenuID, stretch=0, alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.menuHdrLayout.addWidget(self.lblmenuName, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.menuLayout.addLayout(self.menuHdrLayout,0,0,1,3)
        
        self.lblmenuID.setFont(QFont("Arial",8))
        self.lblmenuID.setMargin(10)
        self.lblmenuName.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.lblmenuName.setFont(QFont("Century Gothic", 24))
        # self.menuName.setMargin(20)
        self.lblmenuName.setWordWrap(False)
        
        for bNum in range(_NUM_menuBTNperCOL):
            self.menuButton[bNum] = self.menuBUTTON(bNum+1)
            self.menuButton[bNum+_NUM_menuBTNperCOL] = self.menuBUTTON(bNum+1+_NUM_menuBTNperCOL)
            
            self.menuLayout.addWidget(self.menuButton[bNum],bNum+2,0)
            self.menuLayout.addWidget(self.menuButton[bNum+_NUM_menuBTNperCOL],bNum+2,2)
            
            self.menuButton[bNum].setMinimumWidth(_menu_BTNWIDTH_min), self.menuButton[bNum].setMaximumWidth(_menu_BTNWIDTH_max)
            self.menuButton[bNum+_NUM_menuBTNperCOL].setMinimumWidth(_menu_BTNWIDTH_min), self.menuButton[bNum+_NUM_menuBTNperCOL].setMaximumWidth(_menu_BTNWIDTH_max)
            
            self.menuButton[bNum].clicked.connect(self.handleMenuButtonClick)
            self.menuButton[bNum+_NUM_menuBTNperCOL].clicked.connect(self.handleMenuButtonClick)
        # endfor
            
        self.loadMenu()
    # __init__

    def open_childScreen(self, window_id:str, childScreen: QWidget):
        if window_id not in self.childScreens:
            childScreen.setProperty('id', window_id)
            childScreen.setAttribute(Qt.WA_DeleteOnClose)
            childScreen.destroyed.connect(lambda scrn: self.childScreens.pop(scrn.property('id')))
            self.childScreens[window_id] = childScreen
            childScreen.show()

    def clearoutMenu(self):
        self.lblmenuID.setText("")
        self.lblmenuName.setText("")
        for bNum in range(_NUM_menuBTNperCOL):
            self.menuButton[bNum].setText("\n\n")
            self.menuButton[bNum].setEnabled(False)
            self.menuButton[bNum+_NUM_menuBTNperCOL].setText("\n\n")
            self.menuButton[bNum+_NUM_menuBTNperCOL].setEnabled(False)
    
    def displayMenu(self, menuGroup:int, menuID:int, menuItems:Dict[int,Dict]):
        self.lblmenuID.setText(f'{menuGroup},{menuID}\n{sysver["DEV"]}')
        self.lblmenuName.setText(str(menuItems[0]['OptionText']))
        for n in range(_NUM_menuBUTTONS):
            if n+1 in menuItems:
                self.menuButton[n].setText(f'\n{menuItems[n+1]["OptionText"]}\n')
                self.menuButton[n].setEnabled(True)
            else:
                self.menuButton[n].setText(f'\n\n')
                self.menuButton[n].setEnabled(False)
                pass
     
    def loadMenu(self, menuGroup: int = menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            menuGroup = SRC.dfltMenuGroup()
            pass
        if menuID==self._DFLT_menuID:
            menuID = SRC.dfltMenuID_forGroup(menuGroup)
    
        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDict(menuGroup, menuID)
            self.displayMenu(menuGroup, menuID, self.currentMenu)
        else:
            # menu doesn't exist; say so
            msg = QMessageBox(self)
            msg.setWindowTitle('Menu Doesn\'t Exist')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Menu {menuID} does\'t exist!')
            msg.open()
    
    @Slot()
    def handleMenuButtonClick(self):
        pressedBtn = self.sender()  # sender() should be a menuBUTTON
        pressedBtnNum = pressedBtn.btnNumber
        menuItem = self.currentMenu[pressedBtnNum]
        # print(f'{menuItem}')
        # return
        CommandNum = menuItem['Command']
        CommandArg = menuItem['Argument']
        if MENUCOMMANDS.get(CommandNum) == 'LoadMenu' :
            CommandArg = int(CommandArg)
            self.loadMenu(self.menuGroup, CommandArg)
        elif MENUCOMMANDS.get(CommandNum) == 'FormBrowse' \
          or MENUCOMMANDS.get(CommandNum) == 'OpenTable' :
            frm:QWidget = menucommand_handlers.FormBrowse(self, CommandArg)
            if frm: 
                self.open_childScreen(CommandArg, frm)
        #     frm:QWidget = ShowTable(self, CommandArg)
        #     if frm: 
        #         frm.show()
        # elif MENUCOMMANDS.get(CommandNum) == 'RunCode' :
        #    return
            # fn = getattr(menucommand_handlers, CommandArg)
            # retHTTP = fn(req)
        elif MENUCOMMANDS.get(CommandNum) == 'RunSQLStatement':
            try:
                fn = menucommand_handlers.cMRunSQL
                viewExists = True
            except NameError:
                viewExists = False
            #end try
            if viewExists:
                self.open_childScreen('RunSQL', fn())
            else:  
                formname = f'{formname} exists but view menucommand_handlers.cMRunSQL'
            #endif
        # elif MENUCOMMANDS.get(CommandNum) == 'ConstructSQLStatement':
        #    pass
        # elif MENUCOMMANDS.get(CommandNum)  == 'LoadExtWebPage':
        #     return
            # retHTTP = fn_LoadExtWebPage(req, CommandArg)
        # elif MENUCOMMANDS.get(CommandNum) == 'ChangePW':
        #     return
            # return redirect('change_password')
        elif MENUCOMMANDS.get(CommandNum) == 'EditMenu':
            try:
                fn = cEditMenu
                viewExists = True
            except NameError:
                viewExists = False
            #end try
            if viewExists:
                self.open_childScreen('EditMenu', fn())
            else:  
                formname = f'{formname} exists but view EditMenu'
            #endif
            # return redirect('EditMenu_init')
        # elif MENUCOMMANDS.get(CommandNum) == 'EditParameters':
        #     return
            # return redirect('EditParms')
        # elif MENUCOMMANDS.get(CommandNum) == 'EditGreetings':
        #     return
            # return redirect('Greetings')
        elif MENUCOMMANDS.get(CommandNum) == 'ExitApplication':
            QApplication.instance().exit()
        elif CommandNum in MENUCOMMANDS:
            msg = QMessageBox(self)
            msg.setWindowTitle('Command Not Implemented')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Command {MENUCOMMANDS.get(CommandNum)} will be implemented later')
            msg.open()
        else:
            # invalid Command Number
            msg = QMessageBox(self)
            msg.setWindowTitle('Invalid Command')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'{CommandNum} is an invalid Command Number!')
            msg.open()
        # case MENUCOMMANDS.get(CommandNum)
    # handleMenuButtonClick

###############################################################
###############################################################


###############################################################
###############################################################
###############################################################


