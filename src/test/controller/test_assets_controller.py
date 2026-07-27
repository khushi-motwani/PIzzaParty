from unittest.mock import patch
from controller.assets_controller import get_all_assets, get_assets_count
from dto.assets_dto import AssetsDTO

@patch('controller.assets_controller.assets_service')
def test_get_all_assets(mock_service, app_context):
    asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", 1)
    asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", 0)

    mock_service.get_all.return_value = [asset1, asset2]
    result = get_all_assets()

    data = result.json
    assert len(data) == 2
    assert data[0]["asset_name"] == "Apple"
    assert data[1]["asset_name"] == "Tesla"
    mock_service.get_all.assert_called_once()

@patch('controller.assets_controller.assets_service')
def test_get_all_assets_empty(mock_service, app_context):
    mock_service.get_all.return_value = []

    result = get_all_assets()

    data = result.json
    assert len(data) == 0
    mock_service.get_all.assert_called_once()

@patch('controller.assets_controller.assets_service')
def test_get_assets_count(mock_service, app_context):
    mock_service.count.return_value = 5

    result = get_assets_count()

    data = result.json
    assert data["count"] == 5
    mock_service.count.assert_called_once()
