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
