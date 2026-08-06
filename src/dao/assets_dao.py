from dao.db_config import get_db_connection
from dto.assets_dto import AssetsDTO
from exception.validation_exceptions import AssetNotFoundException

class AssetsDao:
    def __init__(self, connection_factory=None):
        self.connection_factory = connection_factory or get_db_connection
        self.connection = None
        self.assets = []
        self.total = 0

    def _get_connection(self):
        if self.connection is None:
            self.connection = self.connection_factory()
        return self.connection

    def _reset_connection(self):
        self.connection = None

    def count(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Assets")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        return self.total


    def get_all(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets")
        result = dbcursor.fetchall()

        assets = []
        for row in result:
            asset = AssetsDTO(
                asset_id=row[0],
                asset_name=row[1],
                asset_type=row[2],
                asset_sector=row[3],
                asset_industry=row[4],
                is_favourite=bool(row[5])
            )
            assets.append(asset)
        return assets


    def get_by_id(self, asset_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE asset_id = %s", (asset_id,))
        result = dbcursor.fetchone()

        if result is None:
            raise AssetNotFoundException(asset_id)

        return AssetsDTO(
                asset_id=result[0],
                asset_name=result[1],
                asset_type=result[2],
                asset_sector=result[3],
                asset_industry=result[4],
                is_favourite=bool(result[5])
            )

    def get_all_favourite_assets(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE is_favourite = TRUE ORDER BY asset_name")
        result = dbcursor.fetchall()

        favourite_assets = []
        for row in result:
            asset = AssetsDTO(
                asset_id=row[0],
                asset_name=row[1],
                asset_type=row[2],
                asset_sector=row[3],
                asset_industry=row[4],
                is_favourite=bool(row[5])
            )
            favourite_assets.append(asset)
        return favourite_assets

    def get_assets_by_type(self, asset_type):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE asset_type = %s ORDER BY asset_name", (asset_type,))
        result = dbcursor.fetchall()

        assets_by_type = []
        for row in result:
            asset = AssetsDTO(
                asset_id=row[0],
                asset_name=row[1],
                asset_type=row[2],
                asset_sector=row[3],
                asset_industry=row[4],
                is_favourite=bool(row[5])
            )
            assets_by_type.append(asset)
        return assets_by_type

    def get_assets_by_sector(self, asset_sector):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE asset_sector = %s ORDER BY asset_name", (asset_sector,))
        result = dbcursor.fetchall()

        assets_by_sector = []
        for row in result:
            asset = AssetsDTO(
                            asset_id=row[0],
                            asset_name=row[1],
                            asset_type=row[2],
                            asset_sector=row[3],
                            asset_industry=row[4],
                            is_favourite=bool(row[5])
                        )
            assets_by_sector.append(asset)
        return assets_by_sector

    def get_assets_by_industry(self, asset_industry):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Assets WHERE asset_industry = %s ORDER BY asset_name", (asset_industry,))
        result = dbcursor.fetchall()

        assets_by_industry = []
        for row in result:
            asset = AssetsDTO(
                            asset_id=row[0],
                            asset_name=row[1],
                            asset_type=row[2],
                            asset_sector=row[3],
                            asset_industry=row[4],
                            is_favourite=bool(row[5])
                        )
            assets_by_industry.append(asset)
        return assets_by_industry

    def get_favourite_asset_count(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT COUNT(*) as favourite_count FROM Assets WHERE is_favourite = TRUE")
        result = dbcursor.fetchone()
        return result[0]

    def insert_asset(self, asset_id, asset_name, asset_type, asset_sector, asset_industry, is_favourite):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry, is_favourite) VALUES (%s, %s, %s, %s, %s, %s)",
            (asset_id, asset_name, asset_type, asset_sector, asset_industry, is_favourite)
        )
        self._get_connection().commit()

    def update_asset(self, asset_id, asset_name, asset_type, asset_sector, asset_industry):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "UPDATE Assets SET asset_name = %s, asset_type = %s, asset_sector = %s, asset_industry = %s WHERE asset_id = %s",
            (asset_name, asset_type, asset_sector, asset_industry, asset_id)
        )
        self._get_connection().commit()

    def update_asset_favourite_status(self, asset_id, is_favourite):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "UPDATE Assets SET is_favourite = %s WHERE asset_id = %s",
            (is_favourite, asset_id)
        )
        self._get_connection().commit()

    def delete_asset(self, asset_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "DELETE FROM Assets WHERE asset_id = %s",
            (asset_id,)
        )
        self._get_connection().commit()
