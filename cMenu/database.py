import PySide6
from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

cMenu_dbName = "D:\\AppDev\\datasets\\hbl.sqlite"


# class cMenudb(QSqlDatabase):
#     def __init__(self):
#         dbDriver = 'QSQLITE'
#         connectName = 'con_cMenu'
#         db = QSqlDatabase.addDatabase(dbDriver, connectName)
#         super().__init__(db)
#         # con = PQconnectdb("host=server user=bart password=simpson dbname=springfield")
#         # drv = QPSQLDriver(con)
#         self.setDatabaseName(cMenu_dbName)
#         res = self.open()      # this should be checked for success, but for now, take the errors raised if bad
#         # query = QSqlQuery()
#         # query.exec("SELECT NAME, ID FROM STAFF")        
#         # super().__init__(dbDriver)

from incShip.database import incShipDatabase
#cMenuDatabase = cMenudb()
cMenuDatabase = incShipDatabase

