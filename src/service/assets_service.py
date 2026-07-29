from dao.assets_dao import AssetsDao

class AssetsService:
    def __init__(self):
        self.assets_dao = AssetsDao()

    def get_all(self):
        return self.assets_dao.get_all()

    def count(self):
        return self.assets_dao.count()

    def get_by_id(self, asset_id):
        return self.assets_dao.get_by_id(asset_id)

    def get_all_favourite_assets(self):
        return self.assets_dao.get_all_favourite_assets()

    def get_favourite_asset_count(self):
        return self.assets_dao.get_favourite_asset_count()

    def get_assets_by_type(self, asset_type):
        return self.assets_dao.get_assets_by_type(asset_type)

    def get_assets_by_sector(self, asset_sector):
        return self.assets_dao.get_assets_by_sector(asset_sector)

    def get_assets_by_industry(self, asset_industry):
        return self.assets_dao.get_assets_by_industry(asset_industry)

    def create(self, asset_id, asset_name, asset_type, asset_sector, asset_industry, is_favourite=False):
        return self.assets_dao.insert_asset(asset_id, asset_name, asset_type, asset_sector, asset_industry, is_favourite)

    def update_asset(self, asset_id, asset_name, asset_type, asset_sector, asset_industry):
        self.assets_dao.get_by_id(asset_id)
        self.assets_dao.update_asset(asset_id, asset_name, asset_type, asset_sector, asset_industry)

    def update_favourite_status(self, asset_id, is_favourite):
        self.assets_dao.get_by_id(asset_id)
        self.assets_dao.update_asset_favourite_status(asset_id, is_favourite)

    def delete(self, asset_id):
        self.assets_dao.get_by_id(asset_id)
        self.assets_dao.delete_asset(asset_id)
