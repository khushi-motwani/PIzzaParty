from dao.assets_dao import AssetsDao

class AssetsService:
    def __init__(self):
        self.assets_dao = AssetsDao()

    def get_all(self):
        return self.assets_dao.get_all()

    def count(self):
        return self.assets_dao.count()

    def update_favourite_status(self, asset_id, is_favourite):
        self.assets_dao.get_by_id(asset_id)
        self.assets_dao.update_asset_favourite_status(asset_id, is_favourite)
