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

from cMenu.models import (menuItems, menuGroups, )
from cMenu.menucommand_constants import (MENUCOMMANDS, COMMANDNUMBER, )
from cMenu.utils import (cQFmFldWidg, cComboBoxFromDict )
class Test02a(QWidget):
    def __init__(self, menuitmRec:menuItems, parent:QWidget = None):
        super().__init__(parent)
        
        self.setObjectName('cWidgetMenuItem')
        
        self.currRec = menuitmRec
        
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
        self.lnedtOptionNumber.setProperty('modelField', 'OptionNumber')
        self.lnedtOptionNumber.setValue = self.lnedtOptionNumber.setText
        self.lnedtOptionNumber.setProperty('noedit', True)
        self.lnedtOptionNumber.setReadOnly(True)
        self.lnedtOptionNumber.setFrame(False)
        self.lnedtOptionNumber.setMaximumWidth(25)
        self.lnedtOptionNumber.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.fldOptionText = cQFmFldWidg(QLineEdit, lblText='OptionText: ', modlFld='OptionText', parent=self)
        self.fldOptionText.signalFldChanged.connect(lambda: self.changeField(self.fldOptionText))

        self.fldTopLine = cQFmFldWidg(QCheckBox, lblText='Top Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld='TopLine', parent=self)
        self.fldTopLine.signalFldChanged.connect(lambda newstate: self.changeField(self.fldTopLine))

        self.fldBottomLine = cQFmFldWidg(QCheckBox, lblText='Btm Line', lblChkBxYesNo={True:'YES', False:'NO'}, 
                modlFld='BottomLine', parent=self)
        self.fldBottomLine.signalFldChanged.connect(lambda newstate: self.changeField(self.fldBottomLine))

        self.layoutFormLine1.addWidget(self.lblOptionNumber)
        self.layoutFormLine1.addWidget(self.lnedtOptionNumber)
        # self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addWidget(self.fldOptionText)
        # self.layoutFormLine1.addSpacing(20)
        self.layoutFormLine1.addWidget(self.fldTopLine)
        self.layoutFormLine1.addWidget(self.fldBottomLine)

        ##

        self.layoutFormLine2 = QHBoxLayout()

        self.fldCommand = cQFmFldWidg(cComboBoxFromDict, lblText='Command:', modlFld='Command', 
            choices=vars(COMMANDNUMBER), parent=self)
        self.fldCommand.signalFldChanged.connect(lambda x: self.changeField(self.fldCommand))

        self.fldArgument = cQFmFldWidg(QLineEdit, lblText='Argument: ', modlFld='Argument', parent=self)
        self.fldArgument.signalFldChanged.connect(lambda: self.changeField(self.fldArgument))

        self.fldPWord = cQFmFldWidg(QLineEdit, lblText='Password: ', modlFld='PWord', parent=self)
        self.fldPWord.signalFldChanged.connect(lambda: self.changeField(self.fldPWord))

        self.layoutFormLine2.addWidget(self.fldCommand)
        # self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.fldArgument)
        # self.layoutFormLine2.addSpacing(20)
        self.layoutFormLine2.addWidget(self.fldPWord)

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
                wdgtfld = getattr(wdgt, 'modelField', None)
                if callable(wdgtfld): wdgtfld = wdgtfld()
                if wdgtfld == field.name:
                    # set wdgt value to field_value
                    wdgt.setValue(field_valueStr)

                    break   # we found the widget for this field; we don't need to keep testing widgets
                # endif widget field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
        
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
    
    def copyMenuOption(self, moveit=False):
        ...

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QGroupBox, QRadioButton, QButtonGroup, QLCDNumber, )
from django.db import transaction
from django.db.models import QuerySet
from cMenu.dbmenulist import (MenuRecords, newgroupnewmenu_menulist, newmenu_menulist, )
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)
class Test02(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    
    # don't try to do this here - QWidgets cannot be created before QApplication
    # menuScreen: QWidget = QWidget()
    # menuLayout: QGridLayout = QGridLayout()
    # menuButton: Dict[int, QPushButton] = {}

    class wdgtmenuITEM(Test02a):
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
        self.WmenuItm: Dict[int, Test02.wdgtmenuITEM] = {}
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
# class Test02
    

class Test03():
    def __init__(self):
        # just wanna debug ...
        breakpoint()
        pass
    def setProperty(self, dummy1, dummy2):
        pass


##############################################################
##############################################################
##############################################################

