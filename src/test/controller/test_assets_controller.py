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

@patch('controller.assets_controller.assets_service')
def test_get_asset_by_id(mock_service, app_context, client):
    asset = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, "AAPL")
    mock_service.get_by_id = MagicMock(return_value=asset)

    response = client.get('/assets/AAPL')

    assert response.status_code == 200
    data = response.json
    assert data["asset_name"] == "Apple"
    assert data["asset_id"] == "AAPL"
    mock_service.get_by_id.assert_called_once_with("AAPL")

@patch('controller.assets_controller.assets_service')
def test_get_favourite_assets(mock_service, app_context, client):
    asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", True, "AAPL")
    asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", True, "TSLA")
    mock_service.get_all_favourite_assets = MagicMock(return_value=[asset1, asset2])

    response = client.get('/assets/favourite/all')

    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert data[0]["asset_name"] == "Apple"
    assert data[1]["asset_name"] == "Tesla"
    mock_service.get_all_favourite_assets.assert_called_once()

@patch('controller.assets_controller.assets_service')
def test_get_favourite_assets_count(mock_service, app_context, client):
    mock_service.get_favourite_asset_count = MagicMock(return_value=5)

    response = client.get('/assets/favourite/count')

    assert response.status_code == 200
    data = response.json
    assert data["count"] == 5
    mock_service.get_favourite_asset_count.assert_called_once()

@patch('controller.assets_controller.assets_service')
def test_get_assets_by_type(mock_service, app_context, client):
    asset1 = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, "AAPL")
    asset2 = AssetsDTO("Tesla", "STOCK", "Consumer", "Auto", False, "TSLA")
    mock_service.get_assets_by_type = MagicMock(return_value=[asset1, asset2])

    response = client.get('/assets/type/STOCK')

    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    assert all(asset["asset_type"] == "STOCK" for asset in data)
    mock_service.get_assets_by_type.assert_called_once_with("STOCK")

@patch('controller.assets_controller.assets_service')
def test_get_assets_by_sector(mock_service, app_context, client):
    asset = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, "AAPL")
    mock_service.get_assets_by_sector = MagicMock(return_value=[asset])

    response = client.get('/assets/sector/Technology')

    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["asset_sector"] == "Technology"
    mock_service.get_assets_by_sector.assert_called_once_with("Technology")

@patch('controller.assets_controller.assets_service')
def test_get_assets_by_industry(mock_service, app_context, client):
    asset = AssetsDTO("Apple", "STOCK", "Technology", "Hardware", False, "AAPL")
    mock_service.get_assets_by_industry = MagicMock(return_value=[asset])

    response = client.get('/assets/industry/Hardware')

    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["asset_industry"] == "Hardware"
    mock_service.get_assets_by_industry.assert_called_once_with("Hardware")

@patch('controller.assets_controller.assets_service')
def test_create_asset(mock_service, app_context, client):
    mock_service.create = MagicMock()

    response = client.post(
        '/assets',
        data=json.dumps({
            'asset_id': 'AAPL',
            'asset_name': 'Apple Inc.',
            'asset_type': 'STOCK',
            'asset_sector': 'Technology',
            'asset_industry': 'Hardware'
        }),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = response.json
    assert data["message"] == "Asset created successfully"
    mock_service.create.assert_called_once_with('AAPL', 'Apple Inc.', 'STOCK', 'Technology', 'Hardware', False)

@patch('controller.assets_controller.assets_service')
def test_create_asset_as_favourite(mock_service, app_context, client):
    mock_service.create = MagicMock()

    response = client.post(
        '/assets',
        data=json.dumps({
            'asset_id': 'AAPL',
            'asset_name': 'Apple Inc.',
            'asset_type': 'STOCK',
            'asset_sector': 'Technology',
            'asset_industry': 'Hardware',
            'is_favourite': True
        }),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = response.json
    assert data["message"] == "Asset created successfully"
    mock_service.create.assert_called_once_with('AAPL', 'Apple Inc.', 'STOCK', 'Technology', 'Hardware', True)

@patch('controller.assets_controller.assets_service')
def test_update_asset(mock_service, app_context, client):
    mock_service.update_asset = MagicMock()

    response = client.put(
        '/assets/AAPL',
        data=json.dumps({
            'asset_name': 'Apple Inc. Updated',
            'asset_type': 'STOCK',
            'asset_sector': 'Technology',
            'asset_industry': 'Consumer Electronics'
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Asset updated successfully"
    mock_service.update_asset.assert_called_once_with('AAPL', 'Apple Inc. Updated', 'STOCK', 'Technology', 'Consumer Electronics')

@patch('controller.assets_controller.assets_service')
def test_delete_asset(mock_service, app_context, client):
    mock_service.delete = MagicMock()

    response = client.delete('/assets/AAPL')

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Asset deleted successfully"
    mock_service.delete.assert_called_once_with('AAPL')
