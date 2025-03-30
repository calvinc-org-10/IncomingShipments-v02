from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

incShip_dbName = 'D:\\AppDev\\datasets\\hbl.sqlite'

# class incShipdb(QSqlDatabase):
class incShipdb:
    _instance = None  # Store the singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()  # Correctly call the method after creating instance
        return cls._instance

    def _init_db(self):
        dbDriver = 'QSQLITE'
        connectName = 'con_incShip'

        # Check if the connection already exists
        if QSqlDatabase.contains(connectName):
            self.db = QSqlDatabase.database(connectName)
        else:
            self.db = QSqlDatabase.addDatabase(dbDriver, connectName)
            self.db.setDatabaseName(incShip_dbName)
            if not self.db.open():
                print("Database connection failed:", self.db.lastError().text())

    def connection(self):
        """Returns the QSqlDatabase connection"""
        return self.db

incShipDatabase = incShipdb().connection()