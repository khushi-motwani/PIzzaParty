import pytest
from unittest.mock import MagicMock, patch
from service.assets_service import AssetsService
from dto.assets_dto import AssetsDTO
from exception.validation_exceptions import AssetNotFoundException


class TestAssetsService:
    """Test AssetsService methods."""

    @pytest.fixture
    def service(self):
        """Create service with mocked DAO."""
        with patch('service.assets_service.AssetsDao'):
            return AssetsService()

    @pytest.fixture
    def mock_asset(self):
        """Create a mock asset."""
        return AssetsDTO(
            asset_name="Apple",
            asset_type="STOCK",
            asset_sector="Technology",
            asset_industry="Hardware",
            is_favourite=False,
            asset_id=1
        )

    def test_get_all(self, service):
        """Test get_all returns list of assets."""
        asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, 1)
        asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", True, 2)
        service.assets_dao.get_all = MagicMock(return_value=[asset1, asset2])

        result = service.get_all()

        assert len(result) == 2
        assert result[0].asset_name == "Apple"
        assert result[1].asset_name == "Tesla"
        service.assets_dao.get_all.assert_called_once()

    def test_get_all_empty(self, service):
        """Test get_all returns empty list when no assets."""
        service.assets_dao.get_all = MagicMock(return_value=[])

        result = service.get_all()

        assert result == []
        service.assets_dao.get_all.assert_called_once()

    def test_count(self, service):
        """Test count returns asset count."""
        service.assets_dao.count = MagicMock(return_value=5)

        result = service.count()

        assert result == 5
        service.assets_dao.count.assert_called_once()

    def test_count_zero(self, service):
        """Test count returns 0 when no assets."""
        service.assets_dao.count = MagicMock(return_value=0)

        result = service.count()

        assert result == 0

    def test_update_favourite_status_success(self, service, mock_asset):
        """Test update_favourite_status successfully updates asset."""
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.assets_dao.update_asset_favourite_status = MagicMock()

        service.update_favourite_status(1, True)

        service.assets_dao.get_by_id.assert_called_once_with(1)
        service.assets_dao.update_asset_favourite_status.assert_called_once_with(1, True)

    def test_update_favourite_status_to_false(self, service, mock_asset):
        """Test update_favourite_status can set is_favourite to False."""
        mock_asset.is_favourite = True
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.assets_dao.update_asset_favourite_status = MagicMock()

        service.update_favourite_status(1, False)

        service.assets_dao.get_by_id.assert_called_once_with(1)
        service.assets_dao.update_asset_favourite_status.assert_called_once_with(1, False)

    def test_update_favourite_status_not_found(self, service):
        """Test update_favourite_status raises exception when asset not found."""
        service.assets_dao.get_by_id = MagicMock(
            side_effect=AssetNotFoundException(999)
        )

        with pytest.raises(AssetNotFoundException):
            service.update_favourite_status(999, True)

        service.assets_dao.get_by_id.assert_called_once_with(999)
        service.assets_dao.update_asset_favourite_status.assert_not_called()

    def test_get_by_id_success(self, service, mock_asset):
        """Test get_by_id returns asset."""
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)

        result = service.get_by_id(1)

        assert result.asset_id == 1
        assert result.asset_name == "Apple"
        service.assets_dao.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self, service):
        """Test get_by_id raises exception when asset not found."""
        service.assets_dao.get_by_id = MagicMock(
            side_effect=AssetNotFoundException(999)
        )

        with pytest.raises(AssetNotFoundException):
            service.get_by_id(999)

    def test_get_all_favourite_assets(self, service):
        """Test get_all_favourite_assets returns list of favourite assets."""
        asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", True, 1)
        asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", True, 2)
        service.assets_dao.get_all_favourite_assets = MagicMock(return_value=[asset1, asset2])

        result = service.get_all_favourite_assets()

        assert len(result) == 2
        assert result[0].is_favourite is True
        assert result[1].is_favourite is True
        service.assets_dao.get_all_favourite_assets.assert_called_once()

    def test_get_all_favourite_assets_empty(self, service):
        """Test get_all_favourite_assets returns empty list."""
        service.assets_dao.get_all_favourite_assets = MagicMock(return_value=[])

        result = service.get_all_favourite_assets()

        assert result == []

    def test_get_favourite_asset_count(self, service):
        """Test get_favourite_asset_count returns count."""
        service.assets_dao.get_favourite_asset_count = MagicMock(return_value=3)

        result = service.get_favourite_asset_count()

        assert result == 3

    def test_get_assets_by_type(self, service):
        """Test get_assets_by_type returns assets of specific type."""
        asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, 1)
        asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", False, 2)
        service.assets_dao.get_assets_by_type = MagicMock(return_value=[asset1, asset2])

        result = service.get_assets_by_type("STOCK")

        assert len(result) == 2
        assert result[0].asset_type == "STOCK"
        service.assets_dao.get_assets_by_type.assert_called_once_with("STOCK")

    def test_get_assets_by_sector(self, service):
        """Test get_assets_by_sector returns assets of specific sector."""
        asset = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, 1)
        service.assets_dao.get_assets_by_sector = MagicMock(return_value=[asset])

        result = service.get_assets_by_sector("Technology")

        assert len(result) == 1
        assert result[0].asset_sector == "Technology"
        service.assets_dao.get_assets_by_sector.assert_called_once_with("Technology")

    def test_get_assets_by_industry(self, service):
        """Test get_assets_by_industry returns assets of specific industry."""
        asset = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, 1)
        service.assets_dao.get_assets_by_industry = MagicMock(return_value=[asset])

        result = service.get_assets_by_industry("Hardware")

        assert len(result) == 1
        assert result[0].asset_industry == "Hardware"
        service.assets_dao.get_assets_by_industry.assert_called_once_with("Hardware")
