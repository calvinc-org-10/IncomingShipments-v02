from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

incShip_dbName = 'W:\\Logistics\\db\\hbl.sqlite'


class incShipdb(QSqlDatabase):
    def __init__(self):
        dbDriver = 'QSQLITE'
        connectName = 'con_incShip'
        db = QSqlDatabase.addDatabase(dbDriver, connectName)
        super().__init__(db)
        # con = PQconnectdb("host=server user=bart password=simpson dbname=springfield")
        # drv = QPSQLDriver(con)
        self.setDatabaseName(incShip_dbName)
        res = self.open()      # this should be checked for success, but for now, take the errors raised if bad
        # query = QSqlQuery()
        # query.exec("SELECT NAME, ID FROM STAFF")        
        # super().__init__(dbDriver)

incShipDatabase = incShipdb()