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
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QHBoxLayout, 
    QDialog, QMessageBox, 
    QPushButton, QDialogButtonBox, QLabel, QFrame,
    QSizePolicy, 
    )
from PySide6.QtSvgWidgets import QSvgWidget

from .dbmenulist import MenuRecords
from menuformname_viewMap import FormNameToURL_Map
from sysver import sysver
from .menucommand_handlers import MENUCOMMANDS, COMMANDNUMBER

# standard window and related sizes
# copied from main app's forms module
std_windowsize = QSize(1120,720)
std_popdialogsize=QSize(400,300)

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

class cMenu(QWidget):
    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    menuGroup:int = _DFLT_menuGroup
    menuID:int = _DFLT_menuID
    
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
        self.menuButton: Dict[int, self.menuBUTTON] = {}
        self.menuHdrLayout: QHBoxLayout = QHBoxLayout()
        self.menuID: QLabel = QLabel("")
        self.menuName: QLabel = QLabel("")
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
        
        self.menuHdrLayout.addWidget(self.menuID, stretch=0, alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.menuHdrLayout.addWidget(self.menuName, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.menuLayout.addLayout(self.menuHdrLayout,0,0,1,3)
        
        self.menuID.setFont(QFont("Arial",8))
        self.menuID.setMargin(10)
        self.menuName.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.menuName.setFont(QFont("Century Gothic", 24))
        # self.menuName.setMargin(20)
        self.menuName.setWordWrap(False)
        
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
        self.menuID.setText("")
        self.menuName.setText("")
        for bNum in range(_NUM_menuBTNperCOL):
            self.menuButton[bNum].setText("\n\n")
            self.menuButton[bNum].setEnabled(False)
            self.menuButton[bNum+_NUM_menuBTNperCOL].setText("\n\n")
            self.menuButton[bNum+_NUM_menuBTNperCOL].setEnabled(False)
    
    def displayMenu(self, menuGroup:int, menuID:int, menuItems:Dict[int,Dict]):
        self.menuID.setText(f'{menuGroup},{menuID}\n{sysver["DEV"]}')
        self.menuName.setText(str(menuItems[0]['OptionText']))
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
    
        self.menuGroup = menuGroup
        
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
            frm:QWidget = FormBrowse(self, CommandArg)
            if frm: 
                self.open_childScreen(CommandArg, frm)
        #     frm:QWidget = ShowTable(self, CommandArg)
        #     if frm: 
        #         frm.show()
        # elif MENUCOMMANDS.get(CommandNum) == 'RunCode' :
        #    return
            # fn = getattr(menucommand_handlers, CommandArg)
            # retHTTP = fn(req)
        # elif MENUCOMMANDS.get(CommandNum) == 'RunSQLStatement':
        #     return
            # return redirect('RunSQL')
        # elif MENUCOMMANDS.get(CommandNum) == 'ConstructSQLStatement':
        #    pass
        # elif MENUCOMMANDS.get(CommandNum)  == 'LoadExtWebPage':
        #     return
            # retHTTP = fn_LoadExtWebPage(req, CommandArg)
        # elif MENUCOMMANDS.get(CommandNum) == 'ChangePW':
        #     return
            # return redirect('change_password')
        # elif MENUCOMMANDS.get(CommandNum) == 'EditMenu':
        #     return
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


class UnderConstruction_Dialog(QDialog):
    def __init__(self, parent:QWidget = None, constructionMsg:str = '', f:Qt.WindowType = Qt.WindowType.Dialog):
        super().__init__(parent, f)

        if not self.objectName():
            self.setObjectName(u"Dialog")
        self.resize(std_popdialogsize)
        self.setWindowTitle('Not Built Yet')
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 260, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)
        self.constrsign = QSvgWidget('assets/svg/under-construction-barrier-icon.svg',self)
        self.constrsign.setObjectName(u"constrwidget")
        self.constrsign.setGeometry(QRect(10, 60, 381, 191))
        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 381, 51))
        font = QFont()
        font.setPointSize(12)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setText(constructionMsg)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

        QMetaObject.connectSlotsByName(self)
    # __init__


