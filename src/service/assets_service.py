import logging
from dao.assets_dao import AssetsDao

logger = logging.getLogger('pizzaparty')

class AssetsService:
    def __init__(self):
        self.assets_dao = AssetsDao()

    def get_all(self):
        logger.debug("Retrieving all assets")
        return self.assets_dao.get_all()

    def count(self):
        logger.debug("Counting total assets")
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

    def update_favourite_status(self, asset_id, is_favourite):
        self.assets_dao.get_by_id(asset_id)
        self.assets_dao.update_asset_favourite_status(asset_id, is_favourite)
