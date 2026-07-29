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
