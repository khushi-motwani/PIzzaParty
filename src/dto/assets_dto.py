class AssetsDTO:
    def __init__(self, asset_name, asset_id=None, asset_type="UNKNOWN", asset_sector="UNKNOWN", asset_industry="UNKNOWN", is_favourite=False):
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.asset_sector = asset_sector
        self.asset_industry = asset_industry
        self.is_favourite = is_favourite

    def __str__(self):
        return f"AssetsDTO(asset_id={self.asset_id}, asset_name={self.asset_name}, asset_type={self.asset_type}, asset_sector={self.asset_sector}, asset_industry={self.asset_industry}, is_favourite={self.is_favourite})"

    def to_dict(self):
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "asset_sector": self.asset_sector,
            "asset_industry": self.asset_industry,
            "is_favourite": self.is_favourite
        }
