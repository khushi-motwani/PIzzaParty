from dao.db_config import get_db_connection
from dto.assets_dto import AssetsDTO
from exception.validation_exceptions import AssetNotFoundException

class AssetsDao:
    def __init__(self):
        self.connection = get_db_connection()
        self.assets = []
        self.total = 0


    def count(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Assets")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        return self.total


    def get_all(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT * FROM Assets")
        result = dbcursor.fetchall()

        for row in result:
            asset = AssetsDTO(row[1], row[2], row[3], row[4], row[5], row[0])
            self.assets.append(asset)
        return self.assets


    def get_by_id(self, asset_id):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE asset_id = %s", (asset_id,))
        result = dbcursor.fetchone()

        if result is None:
            raise AssetNotFoundException(asset_id)

        return AssetsDTO(result[1], result[2], result[3], result[4], result[5], result[0])
