
# from django.db import models

from random import randint

from PySide6.QtSql import (QSqlRelation, ) # QSqlQuery, )
from .utils import (cQSqlTableModel, cQSqlRelationalTableModel, )

from .database import cMenuDatabase
from .menucommand_constants import MENUCOMMANDS


class menuGroups(cQSqlTableModel):
    """
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "GroupName" varchar(100) NOT NULL UNIQUE, 
    "GroupInfo" varchar(250) NOT NULL);
    """
    def __init__(self, parent = None):
        super().__init__(parent, cMenuDatabase)
        self.setTable('cMenu_menugroups')
    

class menuItems(cQSqlRelationalTableModel):
    """
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "MenuID" smallint NOT NULL, 
    "OptionNumber" smallint NOT NULL, 
    "OptionText" varchar(250) NOT NULL, 
    "Command" integer NULL, 
    "Argument" varchar(250) NOT NULL, 
    "PWord" varchar(250) NOT NULL, 
    "TopLine" bool NULL, 
    "BottomLine" bool NULL, 
    "MenuGroup_id" bigint NULL REFERENCES "cMenu_menugroups" ("id") DEFERRABLE INITIALLY DEFERRED, 
        CONSTRAINT "mnuItUNQ_mGrp_mID_OptNum" UNIQUE ("MenuGroup_id", "MenuID", "OptionNumber"));
    """
    def __init__(self, parent = None):
        super().__init__(parent, cMenuDatabase)
        self.setTable('cMenu_menuitems')
        self.setRelation(self.fieldIndex('MenuGroup_id'), QSqlRelation('cMenu_menugroups', 'id', 'GroupName'))
        # set sort order
        # ordering = ['MenuGroup','MenuID', 'OptionNumber']
    

class cParameters(cQSqlTableModel):
    """
    "ParmName" varchar(100) NOT NULL PRIMARY KEY, 
    "ParmValue" varchar(512) NOT NULL, 
    "UserModifiable" bool NOT NULL, 
    "Comments" varchar(512) NOT NULL);
    """
    def __init__(self, parent = None):
        super().__init__(parent, cMenuDatabase)
        self.setTable('cMenu_cparameters')
    
def getcParm(req, parmname):
    r = cParameters()
    r.setFilter(f'ParmName="{parmname}"')
    if r.select():
        return r.record(0).value('ParmValue')
    else:
        return ''

def setcParm(req, parmname, parmvalue):
    #FIXMEFIXMERESTARTHERE
    P, crFlag = cParameters.objects.get_or_create(ParmName=parmname)
    P.ParmValue = parmvalue
    P.save()


class cGreetings(cQSqlTableModel):
    """
    id = models.AutoField(primary_key=True)
    Greeting = models.CharField(max_length=2000)
    """
    def __init__(self, parent = None):
        super().__init__(parent, cMenuDatabase)
        self.setTable('cMenu_cgreetings')
    def randomGreeting(self) -> str:
        # do better
        self.select()
        n = randint(1,self.rowCount()) - 1
        return self.record(n).value('Greeting')
