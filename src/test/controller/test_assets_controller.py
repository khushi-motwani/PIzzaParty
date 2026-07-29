from unittest.mock import patch, MagicMock
from controller.assets_controller import get_all_assets, get_assets_count, update_favourite_status
from dto.assets_dto import AssetsDTO
import json

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

@patch('controller.assets_controller.assets_service')
def test_update_favourite_status_success(mock_service, app_context, client):
    mock_service.update_favourite_status = MagicMock()

    response = client.put(
        '/assets/favourite',
        data=json.dumps({'asset_id': 1, 'is_favourite': True}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Favourite status updated successfully"
    mock_service.update_favourite_status.assert_called_once_with(1, True)

@patch('controller.assets_controller.assets_service')
def test_update_favourite_status_to_false(mock_service, app_context, client):
    mock_service.update_favourite_status = MagicMock()

    response = client.put(
        '/assets/favourite',
        data=json.dumps({'asset_id': 2, 'is_favourite': False}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Favourite status updated successfully"
    mock_service.update_favourite_status.assert_called_once_with(2, False)
