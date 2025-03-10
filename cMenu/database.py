from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

cMenu_dbName = 'W:\\Logistics\\db\\hbl.sqlite'


class cMenudb(QSqlDatabase):
    def __init__(self):
        dbDriver = 'QSQLITE'
        connectName = 'con_cMenu'
        super().__init__()
        # con = PQconnectdb("host=server user=bart password=simpson dbname=springfield")
        # drv = QPSQLDriver(con)
        self.addDatabase(dbDriver, connectName)
        self.setDatabaseName(cMenu_dbName)
        self.open()      # this should be checked for success, but for now, take the errors raised if bad
        # query = QSqlQuery()
        # query.exec("SELECT NAME, ID FROM STAFF")        
        # super().__init__(dbDriver)

cMenuDatabase = cMenudb()